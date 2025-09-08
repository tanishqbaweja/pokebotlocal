import discord
from discord.ext import commands
import json
import asyncio

class MoveLearning(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pending_moves = {}  # user_id: {pokemon_id, new_move, level, species_name, current_moves}
        self.load_levelup_moves()
        
    def load_levelup_moves(self):
        try:
            with open('levelup_moves.json', 'r') as f:
                self.levelup_moves = json.load(f)
        except FileNotFoundError:
            self.levelup_moves = {}
    
    async def initialize_pokemon_moves(self, pokemon_id, species_id, level):
        """Initialize moves for newly created Pokemon based on their level"""
        from data.complete_pokemon_data import COMPLETE_POKEMON_DATA
        species_data = COMPLETE_POKEMON_DATA.get(species_id)
        if not species_data:
            return
            
        species_name = species_data['name']
        if species_name not in self.levelup_moves:
            return
            
        # Get all moves the Pokemon should know at this level
        moves_to_know = []
        for check_level in range(1, level + 1):
            level_str = str(check_level)
            if level_str in self.levelup_moves[species_name]:
                raw_moves = self.levelup_moves[species_name][level_str]
                if isinstance(raw_moves, list):
                    for move in raw_moves:
                        converted_move = self._convert_move_name(move)
                        if converted_move not in moves_to_know:
                            moves_to_know.append(converted_move)
                else:
                    converted_move = self._convert_move_name(raw_moves)
                    if converted_move not in moves_to_know:
                        moves_to_know.append(converted_move)
        
        # Take the last 4 moves (most recent)
        final_moves = moves_to_know[-4:] if len(moves_to_know) > 4 else moves_to_know
        
        # Update Pokemon with these moves
        move_updates = {}
        for i, move in enumerate(final_moves, 1):
            move_updates[f'move{i}'] = move
            
        if move_updates:
            set_clause = ', '.join([f"{col} = ${i+2}" for i, col in enumerate(move_updates.keys())])
            values = [pokemon_id] + list(move_updates.values())
            await self.bot.db.execute(f"UPDATE pokemon SET {set_clause} WHERE id = $1", *values)
            
    @commands.Cog.listener()
    async def on_pokemon_level_up(self, pokemon_id, old_level, new_level):
        # Check for moves learned between old_level and new_level
        pokemon = await self.bot.db.fetchrow("SELECT * FROM pokemon WHERE id = $1", pokemon_id)
        if not pokemon:
            return
            
        from data.complete_pokemon_data import COMPLETE_POKEMON_DATA
        species_data = COMPLETE_POKEMON_DATA.get(pokemon['species_id'])
        if not species_data:
            return
            
        species_name = species_data['name']
        
        if species_name not in self.levelup_moves:
            return
            
        moves_to_learn = []
        for level in range(old_level + 1, new_level + 1):
            level_str = str(level)
            if level_str in self.levelup_moves[species_name]:
                raw_moves = self.levelup_moves[species_name][level_str]
                if isinstance(raw_moves, list):
                    converted_moves = [self._convert_move_name(move) for move in raw_moves]
                    moves_to_learn.extend(converted_moves)
                else:
                    moves_to_learn.append(self._convert_move_name(raw_moves))
                
        if not moves_to_learn:
            return
            
        # Check current moves
        current_moves = [pokemon['move1'], pokemon['move2'], pokemon['move3'], pokemon['move4']]
        current_moves = [move for move in current_moves if move]
        
        for new_move in moves_to_learn:
            if new_move in current_moves:
                continue  # Already knows this move
                
            if len(current_moves) < 4:
                # Learn move automatically
                slot = len(current_moves) + 1
                column_map = {1: 'move1', 2: 'move2', 3: 'move3', 4: 'move4'}
                await self.bot.db.execute(
                    f"UPDATE pokemon SET {column_map[slot]} = $1 WHERE id = $2",
                    new_move, pokemon_id
                )
                current_moves.append(new_move)
                
                # Notify user of automatic learning
                try:
                    user_obj = self.bot.get_user(pokemon['owner_id'])
                    if user_obj:
                        await user_obj.send(f"🎓 **{species_name}** learned **{new_move.replace('_', ' ').title()}**!")
                except:
                    pass
            else:
                # Need to replace a move - add to pending
                self.pending_moves[pokemon['owner_id']] = {
                    'pokemon_id': pokemon_id,
                    'new_move': new_move,
                    'level': new_level,
                    'species_name': species_name,
                    'current_moves': current_moves.copy()
                }
                
                # Show move choice immediately
                await self._show_move_choice(pokemon['owner_id'])
                break  # Only handle one move at a time
                    
    async def _show_move_choice(self, user_id):
        """Show move choice interface to user"""
        if user_id not in self.pending_moves:
            return
            
        pending = self.pending_moves[user_id]
        
        try:
            user_obj = self.bot.get_user(user_id)
            if not user_obj:
                return
                
            embed = discord.Embed(
                title="🎓 Move Learning Choice",
                description=f"Your **{pending['species_name']}** wants to learn **{pending['new_move'].replace('_', ' ').title()}**, but already knows 4 moves!\n\nChoose one move to forget:",
                color=0xffa500
            )
            
            view = MoveChoiceView(self.bot, user_id, pending)
            await user_obj.send(embed=embed, view=view)
        except Exception as e:
            print(f"Error showing move choice: {e}")
            
    @commands.hybrid_command(name="choosemove", description="Choose which move to replace when learning a new move")
    async def choose_move_command(self, ctx):
        user_id = ctx.author.id
        if user_id not in self.pending_moves:
            await ctx.send("You don't have any pending move learning decisions.", ephemeral=True)
            return
            
        await self._show_move_choice(user_id)
        await ctx.send("Move choice sent to your DMs!", ephemeral=True)
        
    @commands.hybrid_command(name="forgetmove", description="Skip learning the new move")
    async def forget_move_command(self, ctx):
        user_id = ctx.author.id
        if user_id not in self.pending_moves:
            await ctx.send("You don't have any pending move learning decisions.", ephemeral=True)
            return
            
        pending = self.pending_moves[user_id]
        del self.pending_moves[user_id]
        
        await ctx.send(f"Your **{pending['species_name']}** did not learn **{pending['new_move'].replace('_', ' ').title()}**.", ephemeral=True)
        
    def has_pending_moves(self, user_id):
        return user_id in self.pending_moves
        
    def _convert_move_name(self, move_name):
        """Convert move name from display format to database format"""
        # First, handle exact matches from the JSON file
        exact_conversions = {
            # Direct mappings from levelup_moves.json to database format
            'PoisonPowder': 'poison_powder',
            'Sleep Powder': 'sleep_powder',
            'Stun Spore': 'stun_spore', 
            'DoubleSlap': 'double_slap',
            'SolarBeam': 'solar_beam',
            'ThunderShock': 'thunder_shock',
            'ThunderPunch': 'thunder_punch',
            'ViceGrip': 'vise_grip',
            'Sand-Attack': 'sand_attack',
            'SonicBoom': 'sonic_boom',
            'SmokeScreen': 'smokescreen',
            'Double-Edge': 'double_edge',
            'BubbleBeam': 'bubble_beam',
            'IceBeam': 'ice_beam',
            'IcePunch': 'ice_punch',
            'FirePunch': 'fire_punch',
            'HyperBeam': 'hyper_beam',
            'HyperFang': 'hyper_fang',
            'MegaDrain': 'mega_drain',
            'MegaKick': 'mega_kick',
            'MegaPunch': 'mega_punch',
            'NightShade': 'night_shade',
            'PayDay': 'pay_day',
            'PetalDance': 'petal_dance',
            'PinMissile': 'pin_missile',
            'PoisonGas': 'poison_gas',
            'PoisonSting': 'poison_sting',
            'QuickAttack': 'quick_attack',
            'RazorLeaf': 'razor_leaf',
            'RazorWind': 'razor_wind',
            'RockSlide': 'rock_slide',
            'RockThrow': 'rock_throw',
            'RollingKick': 'rolling_kick',
            'SeismicToss': 'seismic_toss',
            'SkullBash': 'skull_bash',
            'SkyAttack': 'sky_attack',
            'SoftBoiled': 'soft_boiled',
            'SpikeCannon': 'spike_cannon',
            'StringShot': 'string_shot',
            'SuperFang': 'super_fang',
            'TailWhip': 'tail_whip',
            'TakeDown': 'take_down',
            'ThunderWave': 'thunder_wave',
            'TriAttack': 'tri_attack',
            'VineWhip': 'vine_whip',
            'WaterGun': 'water_gun',
            'WingAttack': 'wing_attack',
            'AcidArmor': 'acid_armor',
            'AuroraBeam': 'aurora_beam',
            'BodySlam': 'body_slam',
            'BoneClub': 'bone_club',
            'ConfuseRay': 'confuse_ray',
            'CometPunch': 'comet_punch',
            'DefenseCurl': 'defense_curl',
            'DragonRage': 'dragon_rage',
            'DrillPeck': 'drill_peck',
            'EggBomb': 'egg_bomb',
            'FireBlast': 'fire_blast',
            'FireSpin': 'fire_spin',
            'FocusEnergy': 'focus_energy',
            'FuryAttack': 'fury_attack',
            'FurySwipes': 'fury_swipes',
            'HiJumpKick': 'high_jump_kick',
            'HornAttack': 'horn_attack',
            'HornDrill': 'horn_drill',
            'HydroPump': 'hydro_pump',
            'JumpKick': 'jump_kick',
            'KarateChop': 'karate_chop',
            'LeechLife': 'leech_life',
            'LeechSeed': 'leech_seed',
            'LightScreen': 'light_screen',
            'LovelyKiss': 'lovely_kiss',
            'LowKick': 'low_kick',
            'MirrorMove': 'mirror_move',
            'SwordsDance': 'swords_dance',
            'DreamEater': 'dream_eater',
            'DoubleTeam': 'double_team',
            'DoubleKick': 'double_kick',
            'Hi Jump Kick': 'high_jump_kick',
            'Dizzy Punch': 'dizzy_punch'
        }
        
        # Check for exact match first
        if move_name in exact_conversions:
            return exact_conversions[move_name]
            
        # Convert to lowercase and replace spaces/hyphens with underscores
        converted = move_name.lower().replace(' ', '_').replace('-', '_')
        converted = converted.replace('♀', '_f').replace('♂', '_m')
        converted = converted.replace('.', '').replace("'", '').replace('!', '')
        
        return converted

class MoveChoiceView(discord.ui.View):
    def __init__(self, bot, user_id, pending):
        super().__init__(timeout=300)  # 5 minute timeout
        self.bot = bot
        self.user_id = user_id
        self.pending = pending
        
        # Add buttons for each current move
        for i, move in enumerate(pending['current_moves']):
            button = discord.ui.Button(
                label=move.replace('_', ' ').title(),
                style=discord.ButtonStyle.secondary,
                custom_id=f"replace_{i}"
            )
            button.callback = self.make_replace_callback(i, move)
            self.add_item(button)
            
        # Add ignore button
        ignore_button = discord.ui.Button(
            label="Don't Learn Move",
            style=discord.ButtonStyle.danger,
            custom_id="ignore"
        )
        ignore_button.callback = self.ignore_callback
        self.add_item(ignore_button)
        
    def make_replace_callback(self, slot, old_move):
        async def replace_callback(interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("This isn't your choice!", ephemeral=True)
                return
                
            # Replace the move
            move_slot = slot + 1
            if move_slot not in [1, 2, 3, 4]:
                await interaction.response.send_message("Invalid move slot!", ephemeral=True)
                return
                
            column_map = {1: 'move1', 2: 'move2', 3: 'move3', 4: 'move4'}
            await self.bot.db.execute(
                f"UPDATE pokemon SET {column_map[move_slot]} = $1 WHERE id = $2",
                self.pending['new_move'], self.pending['pokemon_id']
            )
            
            # Remove from pending
            move_learning_cog = self.bot.get_cog('MoveLearning')
            if move_learning_cog and self.user_id in move_learning_cog.pending_moves:
                del move_learning_cog.pending_moves[self.user_id]
            
            embed = discord.Embed(
                title="🎓 Move Learned!",
                description=f"Your {self.pending['species_name']} forgot **{old_move.replace('_', ' ').title()}** and learned **{self.pending['new_move'].replace('_', ' ').title()}**!",
                color=0x00ff00
            )
            
            self.clear_items()
            await interaction.response.edit_message(embed=embed, view=self)
            
        return replace_callback
        
    async def ignore_callback(self, interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your choice!", ephemeral=True)
            return
            
        # Remove from pending
        move_learning_cog = self.bot.get_cog('MoveLearning')
        if move_learning_cog and self.user_id in move_learning_cog.pending_moves:
            del move_learning_cog.pending_moves[self.user_id]
        
        embed = discord.Embed(
            title="Move Not Learned",
            description=f"Your {self.pending['species_name']} did not learn **{self.pending['new_move'].replace('_', ' ').title()}**.",
            color=0xe74c3c
        )
        
        self.clear_items()
        await interaction.response.edit_message(embed=embed, view=self)
        
    async def on_timeout(self):
        # Clear buttons when timeout occurs
        self.clear_items()
        # Note: Can't edit message here as we don't have message reference

async def setup(bot):
    await bot.add_cog(MoveLearning(bot))