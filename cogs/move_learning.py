import discord
from discord.ext import commands
import json
import asyncio

class MoveLearning(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pending_moves = {}  # user_id: {pokemon_id, new_move, level}
        self.load_levelup_moves()
        
    def load_levelup_moves(self):
        try:
            with open('levelup_moves.json', 'r') as f:
                self.levelup_moves = json.load(f)
        except FileNotFoundError:
            self.levelup_moves = {}
            
    @commands.Cog.listener()
    async def on_pokemon_level_up(self, pokemon, old_level, new_level, channel_id=None):
        pokemon_id = pokemon['id']
        # Check for moves learned between old_level and new_level
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
                # Convert move names to proper format
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
        
        channel = self.bot.get_channel(channel_id) if channel_id else None

        for new_move in moves_to_learn:
            if new_move in current_moves:
                continue  # Already knows this move
                
            if len(current_moves) < 4:
                # Learn move automatically - validate slot number for security
                slot = len(current_moves) + 1
                if slot not in [1, 2, 3, 4]:
                    continue
                    
                column_map = {1: 'move1', 2: 'move2', 3: 'move3', 4: 'move4'}
                await self.bot.db.execute(
                    f"UPDATE pokemon SET {column_map[slot]} = $1 WHERE id = $2",
                    new_move, pokemon_id
                )
                current_moves.append(new_move)
                
                # Notify user of automatic learning in the channel
                if channel:
                    embed = discord.Embed(
                        title="Move Learned!",
                        description=f"<@{pokemon['owner_id']}>'s {species_name} learned **{new_move.replace('_', ' ').title()}**!",
                        color=0x00ff00
                    )
                    await channel.send(embed=embed)
            else:
                # Need to replace a move - add to pending
                self.pending_moves[pokemon['owner_id']] = {
                    'pokemon_id': pokemon_id,
                    'new_move': new_move,
                    'level': new_level,
                    'species_name': species_name
                }
                
                # Notify user they need to choose in the channel
                if channel:
                    current_move_list = "\n".join([f"• {move.replace('_', ' ').title()}" for move in current_moves])
                    embed = discord.Embed(
                        title="🎓 Move Learning Choice Required!",
                        description=f"{channel.guild.get_member(pokemon['owner_id']).mention}, your **{species_name}** wants to learn **{new_move.replace('_', ' ').title()}**!\n\n"
                                  f"**Current Moves:**\n{current_move_list}\n\n"
                                  f"Use `/choosemove` to decide which move to replace, or `/forgetmove` to skip learning this move.\n\n"
                                  f"⚠️ **You cannot battle or trade until you make this decision!**",
                        color=0xffa500
                    )
                    await channel.send(embed=embed)
                    
    @commands.hybrid_command(name="choosemove", description="Choose which move to replace when learning a new move")
    async def choose_move(self, ctx):
        user_id = ctx.author.id
        
        if user_id not in self.pending_moves:
            await ctx.send("You don't have any pending move choices!", ephemeral=True)
            return
            
        pending = self.pending_moves[user_id]
        
        # Validate pending data structure
        required_keys = ['pokemon_id', 'new_move', 'species_name']
        if not all(key in pending for key in required_keys):
            del self.pending_moves[user_id]
            await ctx.send("Invalid pending move data. Please try again.", ephemeral=True)
            return
            
        pokemon = await self.bot.db.fetchrow("SELECT * FROM pokemon WHERE id = $1", pending['pokemon_id'])
        
        if not pokemon:
            del self.pending_moves[user_id]
            await ctx.send("Pokemon not found!", ephemeral=True)
            return
            
        current_moves = [pokemon['move1'], pokemon['move2'], pokemon['move3'], pokemon['move4']]
        current_moves = [move for move in current_moves if move]
        
        embed = discord.Embed(
            title=f"Choose Move to Replace",
            description=f"Your {pending['species_name']} wants to learn **{pending['new_move']}**.\n\n"
                      f"Which move should be forgotten?",
            color=0x3498db
        )
        
        view = MoveChoiceView(self.bot.db, user_id, pending, current_moves)
        await ctx.send(embed=embed, view=view, ephemeral=True)
        
    @commands.hybrid_command(name="forgetmove", description="Skip learning the new move")
    async def forget_move(self, ctx):
        user_id = ctx.author.id
        
        if user_id not in self.pending_moves:
            await ctx.send("You don't have any pending move choices!", ephemeral=True)
            return
            
        pending = self.pending_moves[user_id]
        del self.pending_moves[user_id]
        
        embed = discord.Embed(
            title="Move Forgotten",
            description=f"Your {pending['species_name']} did not learn **{pending['new_move']}**.",
            color=0xe74c3c
        )
        await ctx.send(embed=embed, ephemeral=True)
        
    def has_pending_moves(self, user_id):
        return user_id in self.pending_moves
        
    def _convert_move_name(self, move_name):
        """Convert move name from display format to database format"""
        # Convert spaces to underscores, remove special characters, lowercase
        converted = move_name.lower().replace(' ', '_').replace('-', '_')
        converted = converted.replace('♀', '_f').replace('♂', '_m')
        converted = converted.replace('.', '').replace("'", '').replace('!', '')
        
        # Remove common punctuation and handle special characters
        converted = converted.replace("'", '').replace('.', '').replace('!', '')
        
        # Handle special cases - comprehensive mapping
        special_conversions = {
            # Common compound words
            'poisonpowder': 'poison_powder',
            'sleeppowder': 'sleep_powder', 
            'stunspore': 'stun_spore',
            'doubleslap': 'double_slap',
            'solarbeam': 'solar_beam',
            'thundershock': 'thunder_shock',
            'thunderpunch': 'thunder_punch',
            'vicegrip': 'vise_grip',
            'sandattack': 'sand_attack',
            'selfdestruct': 'self_destruct',
            'sonicboom': 'sonic_boom',
            'smokescreen': 'smoke_screen',
            'doubleedge': 'double_edge',
            'doubleteam': 'double_team',
            'doublekick': 'double_kick',
            'bubblebeam': 'bubble_beam',
            'icebeam': 'ice_beam',
            'icepunch': 'ice_punch',
            'firepunch': 'fire_punch',
            'hyperbeam': 'hyper_beam',
            'hyperfang': 'hyper_fang',
            'megadrain': 'mega_drain',
            'megakick': 'mega_kick',
            'megapunch': 'mega_punch',
            'nightshade': 'night_shade',
            'payday': 'pay_day',
            'petaldance': 'petal_dance',
            'pinmissile': 'pin_missile',
            'poisongas': 'poison_gas',
            'poisonsting': 'poison_sting',
            'quickattack': 'quick_attack',
            'razorleaf': 'razor_leaf',
            'razorwind': 'razor_wind',
            'rockslide': 'rock_slide',
            'rockthrow': 'rock_throw',
            'rollingkick': 'rolling_kick',
            'seismictoss': 'seismic_toss',
            'skullbash': 'skull_bash',
            'skyattack': 'sky_attack',
            'softboiled': 'soft_boiled',
            'spikecannon': 'spike_cannon',
            'stringshot': 'string_shot',
            'superfang': 'super_fang',
            'tailwhip': 'tail_whip',
            'takedown': 'take_down',
            'thunderwave': 'thunder_wave',
            'triattack': 'tri_attack',
            'vinewhip': 'vine_whip',
            'watergun': 'water_gun',
            'wingattack': 'wing_attack',
            'acidarmor': 'acid_armor',
            'aurorabeam': 'aurora_beam',
            'bodyslam': 'body_slam',
            'boneclub': 'bone_club',
            'confuseray': 'confuse_ray',
            'cometpunch': 'comet_punch',
            'defensecurl': 'defense_curl',
            'dragonrage': 'dragon_rage',
            'drillpeck': 'drill_peck',
            'eggbomb': 'egg_bomb',
            'fireblast': 'fire_blast',
            'firespin': 'fire_spin',  # Fixed from fire_swing
            'focusenergy': 'focus_energy',
            'furyattack': 'fury_attack',
            'furyswipes': 'fury_swipes',
            'hijumpkick': 'high_jump_kick',
            'hornattack': 'horn_attack',
            'horndrill': 'horn_drill',
            'hydropump': 'hydro_pump',
            'jumpkick': 'jump_kick',
            'karatechop': 'karate_chop',
            'leechlife': 'leech_life',
            'leechseed': 'leech_seed',
            'lightscreen': 'light_screen',
            'lovelykiss': 'lovely_kiss',
            'lowkick': 'low_kick',
            'mirrormove': 'mirror_move',
            
            # Additional common variations
            'thunderbolt': 'thunderbolt',
            'flamethrower': 'flamethrower',
            'earthquake': 'earthquake',
            'psychic': 'psychic',
            'blizzard': 'blizzard',
            'surf': 'surf',
            'strength': 'strength',
            'flash': 'flash',
            'cut': 'cut',
            'fly': 'fly',
            
            # Hyphenated moves
            'hi_jump_kick': 'high_jump_kick',
            'u_turn': 'u_turn',
            
            # Moves with apostrophes or periods
            'kings_rock': 'kings_rock',
            
            # Status moves
            'swordsdance': 'swords_dance',
            'sleeptalk': 'sleep_talk',
            'dreameater': 'dream_eater',
            'substitute': 'substitute',
            'transform': 'transform',
            'metronome': 'metronome',
            'minimize': 'minimize',
            'recover': 'recover',
            'teleport': 'teleport',
            'disable': 'disable',
            'counter': 'counter',
            'mimic': 'mimic',
            'reflect': 'reflect',
            'barrier': 'barrier',
            'haze': 'haze',
            'mist': 'mist',
            'rest': 'rest',
            'conversion': 'conversion',
            'splash': 'splash',
            'sharpen': 'sharpen',
            'withdraw': 'withdraw',
            'harden': 'harden',
            'growl': 'growl',
            'roar': 'roar',
            'sing': 'sing',
            'supersonic': 'supersonic',
            'screech': 'screech',
            'leer': 'leer',
            'glare': 'glare',
            'kinesis': 'kinesis',
            'amnesia': 'amnesia',
            'agility': 'agility',
            'whirlwind': 'whirlwind'
        }
        
        return special_conversions.get(converted, converted)

class MoveChoiceView(discord.ui.View):
    def __init__(self, db, user_id, pending, current_moves):
        super().__init__(timeout=300)
        self.db = db
        self.user_id = user_id
        self.pending = pending
        self.current_moves = current_moves
        
        # Add buttons for each current move
        for i, move in enumerate(current_moves):
            button = discord.ui.Button(
                label=f"Replace {move}",
                style=discord.ButtonStyle.secondary,
                custom_id=f"replace_{i}"
            )
            button.callback = self.make_replace_callback(i, move)
            self.add_item(button)
            
        # Add cancel button
        cancel_button = discord.ui.Button(
            label="Don't Learn Move",
            style=discord.ButtonStyle.danger,
            custom_id="cancel"
        )
        cancel_button.callback = self.cancel_callback
        self.add_item(cancel_button)
        
    def make_replace_callback(self, slot, old_move):
        async def replace_callback(interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("This isn't your choice!", ephemeral=True)
                return
                
            # Replace the move - validate slot number for security
            move_slot = slot + 1
            if move_slot not in [1, 2, 3, 4]:
                await interaction.response.send_message("Invalid move slot!", ephemeral=True)
                return
                
            column_map = {1: 'move1', 2: 'move2', 3: 'move3', 4: 'move4'}
            await self.db.execute(
                f"UPDATE pokemon SET {column_map[move_slot]} = $1 WHERE id = $2",
                self.pending['new_move'], self.pending['pokemon_id']
            )
            
            # Remove from pending
            try:
                move_learning_cog = interaction.client.get_cog('MoveLearning')
                if move_learning_cog and self.user_id in move_learning_cog.pending_moves:
                    del move_learning_cog.pending_moves[self.user_id]
            except Exception as e:
                import logging
                logging.exception(f"Error removing pending move: {e}")
            
            embed = discord.Embed(
                title="Move Learned!",
                description=f"Your {self.pending['species_name']} forgot **{old_move}** and learned **{self.pending['new_move']}**!",
                color=0x00ff00
            )
            
            self.clear_items()
            await interaction.response.edit_message(embed=embed, view=self)
            
        return replace_callback
        
    async def cancel_callback(self, interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your choice!", ephemeral=True)
            return
            
        # Remove from pending
        try:
            move_learning_cog = interaction.client.get_cog('MoveLearning')
            if move_learning_cog and self.user_id in move_learning_cog.pending_moves:
                del move_learning_cog.pending_moves[self.user_id]
        except Exception as e:
            import logging
            logging.exception(f"Error removing pending move: {e}")
        
        embed = discord.Embed(
            title="Move Not Learned",
            description=f"Your {self.pending['species_name']} did not learn **{self.pending['new_move']}**.",
            color=0xe74c3c
        )
        
        self.clear_items()
        await interaction.response.edit_message(embed=embed, view=self)

async def setup(bot):
    await bot.add_cog(MoveLearning(bot))