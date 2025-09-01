import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
from data.gym_data import GYM_LEADERS, ELITE_FOUR, CHAMPION
from data.complete_pokemon_data import COMPLETE_POKEMON_DATA as POKEMON_DATA
from data.complete_moves_data import COMPLETE_MOVES_DATA as MOVES_DATA
from data.moves_data import TYPE_EFFECTIVENESS

class Gym(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_gym_battles = {}
        
    @app_commands.command(name="gym", description="Challenge a gym leader")
    @app_commands.describe(leader="Choose a gym leader to challenge")
    @app_commands.choices(leader=[
        app_commands.Choice(name="Brock (Rock)", value="brock"),
        app_commands.Choice(name="Misty (Water)", value="misty"),
        app_commands.Choice(name="Lt. Surge (Electric)", value="surge"),
        app_commands.Choice(name="Erika (Grass)", value="erika"),
        app_commands.Choice(name="Koga (Poison)", value="koga"),
        app_commands.Choice(name="Sabrina (Psychic)", value="sabrina"),
        app_commands.Choice(name="Blaine (Fire)", value="blaine"),
        app_commands.Choice(name="Giovanni (Ground)", value="giovanni")
    ])
    async def gym_battle(self, interaction: discord.Interaction, leader: str):
        user_id = interaction.user.id
        leader = leader.lower()
            
        # Check for gym battles in this server only
        server_id = interaction.guild.id
        if user_id in self.active_gym_battles:
            battle_cog = self.bot.get_cog('Battle')
            if battle_cog and user_id in battle_cog.active_battles:
                existing_battle = battle_cog.active_battles[user_id]
                if existing_battle.get('server_id') == server_id:
                    await interaction.response.send_message("You're already in a gym battle in this server!", ephemeral=True)
                    return
            
        try:
            # Check user has Pokemon
            party = await self.bot.db.get_user_pokemon(user_id, in_party=True)
            alive_party = [p for p in party if p['current_hp'] > 0] if party else []
            if not alive_party:
                await interaction.response.send_message("You need Pokemon with HP > 0 to challenge a gym!", ephemeral=True)
                return
                
            # Check badge requirements
            user = await self.bot.db.get_user(user_id)
            if not user:
                await interaction.response.send_message("You haven't started your journey yet! Use `/start` to begin.", ephemeral=True)
                return
        except Exception as e:
            import logging
            logging.error(f"Database error in gym battle: {e}")
            await interaction.response.send_message("Database error occurred. Please try again.", ephemeral=True)
            return
        required_badges = list(GYM_LEADERS.keys()).index(leader)
        
        if user['badges'] < required_badges:
            await interaction.response.send_message(f"You must defeat the previous gym leaders first! You have {user['badges']} badges.", ephemeral=True)
            return
            
        # Allow re-battles but mark if it's a rematch
        is_rematch = user['badges'] > required_badges
            
        await self._start_gym_battle(interaction, leader, alive_party[0], is_rematch)
        
    @app_commands.command(name="elite4", description="Challenge the Elite Four")
    @app_commands.describe(member="Choose an Elite Four member to challenge")
    @app_commands.choices(member=[
        app_commands.Choice(name="Lorelei (Ice)", value="lorelei"),
        app_commands.Choice(name="Bruno (Fighting)", value="bruno"),
        app_commands.Choice(name="Agatha (Ghost)", value="agatha"),
        app_commands.Choice(name="Lance (Dragon)", value="lance")
    ])
    async def elite_four(self, interaction: discord.Interaction, member: str):
        user_id = interaction.user.id
        
        # Check for battles in this server only
        server_id = interaction.guild.id
        if user_id in self.active_gym_battles:
            battle_cog = self.bot.get_cog('Battle')
            if battle_cog and user_id in battle_cog.active_battles:
                existing_battle = battle_cog.active_battles[user_id]
                if existing_battle.get('server_id') == server_id:
                    await interaction.response.send_message("You're already in battle in this server!", ephemeral=True)
                    return
            
        # Check badges
        user = await self.bot.db.get_user(user_id)
        if user['badges'] < 8:
            await interaction.response.send_message("You need all 8 gym badges to challenge the Elite Four!", ephemeral=True)
            return
            
        # Allow re-battles
        member_index = list(ELITE_FOUR.keys()).index(member)
        is_rematch = user['badges'] > 8 + member_index
            
        # Check party
        party = await self.bot.db.get_user_pokemon(user_id, in_party=True)
        alive_party = [p for p in party if p['current_hp'] > 0] if party else []
        if not alive_party:
            await interaction.response.send_message("You need Pokemon with HP > 0 to challenge the Elite Four!", ephemeral=True)
            return
            
        member = member.lower()
            
        await self._start_elite_battle(interaction, member, alive_party[0], is_rematch)
        
    @app_commands.command(name="champion", description="Challenge the Champion")
    async def champion_battle(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        
        # Check for battles in this server only
        server_id = interaction.guild.id
        if user_id in self.active_gym_battles:
            battle_cog = self.bot.get_cog('Battle')
            if battle_cog and user_id in battle_cog.active_battles:
                existing_battle = battle_cog.active_battles[user_id]
                if existing_battle.get('server_id') == server_id:
                    await interaction.response.send_message("You're already in battle in this server!", ephemeral=True)
                    return
            
        # Check Elite Four completion
        user = await self.bot.db.get_user(user_id)
        if user['badges'] < 12:  # 8 gyms + 4 Elite Four
            await interaction.response.send_message("You must defeat the Elite Four first!", ephemeral=True)
            return
            
        # Allow re-battles
        is_rematch = user['badges'] >= 13
            
        party = await self.bot.db.get_user_pokemon(user_id, in_party=True)
        alive_party = [p for p in party if p['current_hp'] > 0] if party else []
        if not alive_party:
            await interaction.response.send_message("You need Pokemon with HP > 0 to challenge the Champion!", ephemeral=True)
            return
            
        await self._start_champion_battle(interaction, alive_party[0], is_rematch)
        
    async def _start_gym_battle(self, interaction, leader_name, player_pokemon, is_rematch=False):
        leader_data = GYM_LEADERS[leader_name]
        npc_pokemon = self._create_npc_pokemon(leader_data['team'][0])
        
        # Use PvP battle system
        battle_cog = self.bot.get_cog('Battle')
        if not battle_cog:
            await interaction.response.send_message("Battle system is not available!", ephemeral=True)
            return
            
        try:
            # Create NPC user ID (negative to distinguish from real users)
            npc_user_id = -(1000 + list(GYM_LEADERS.keys()).index(leader_name))
            
            # Store gym battle info
            self.active_gym_battles[interaction.user.id] = {
                'type': 'gym',
                'leader': leader_name,
                'npc_user_id': npc_user_id,
                'npc_team': leader_data['team'],
                'npc_team_index': 0,
                'is_rematch': is_rematch
            }
            
            embed = discord.Embed(
                title=f"Gym Battle vs {leader_data['name']}!",
                description=f"You challenged {leader_data['name']}, the {leader_data['type']}-type gym leader!",
                color=0xe74c3c
            )
            
            await interaction.response.send_message(embed=embed)
            
            # Start battle using PvP system
            await battle_cog.start_battle(
                interaction.channel, interaction.user.id, npc_user_id,
                player_pokemon, npc_pokemon
            )
        except Exception as e:
            import logging
            logging.error(f"Error starting gym battle: {e}")
            if interaction.user.id in self.active_gym_battles:
                del self.active_gym_battles[interaction.user.id]
            await interaction.followup.send("Failed to start gym battle. Please try again.", ephemeral=True)
        
    async def _start_elite_battle(self, interaction, member_name, player_pokemon, is_rematch=False):
        member_data = ELITE_FOUR[member_name]
        npc_pokemon = self._create_npc_pokemon(member_data['team'][0])
        
        # Use PvP battle system
        battle_cog = self.bot.get_cog('Battle')
        if battle_cog:
            # Create NPC user ID (negative to distinguish from real users)
            npc_user_id = -(2000 + list(ELITE_FOUR.keys()).index(member_name))
            
            # Store elite battle info
            self.active_gym_battles[interaction.user.id] = {
                'type': 'elite4',
                'member': member_name,
                'npc_user_id': npc_user_id,
                'npc_team': member_data['team'],
                'npc_team_index': 0,
                'is_rematch': is_rematch
            }
            
            embed = discord.Embed(
                title=f"Elite Four Battle vs {member_data['name']}!",
                description=f"You challenged {member_data['name']} of the Elite Four!",
                color=0x9b59b6
            )
            
            await interaction.response.send_message(embed=embed)
            
            # Start battle using PvP system
            await battle_cog.start_battle(
                interaction.channel, interaction.user.id, npc_user_id,
                player_pokemon, npc_pokemon
            )
        
    async def _start_champion_battle(self, interaction, player_pokemon, is_rematch=False):
        champion_data = CHAMPION['blue']
        npc_pokemon = self._create_npc_pokemon(champion_data['team'][0])
        
        # Use PvP battle system
        battle_cog = self.bot.get_cog('Battle')
        if battle_cog:
            # Create NPC user ID (negative to distinguish from real users)
            npc_user_id = -3000  # Champion ID
            
            # Store champion battle info
            self.active_gym_battles[interaction.user.id] = {
                'type': 'champion',
                'npc_user_id': npc_user_id,
                'npc_team': champion_data['team'],
                'npc_team_index': 0,
                'is_rematch': is_rematch
            }
            
            embed = discord.Embed(
                title="Champion Battle!",
                description="You challenged the Pokemon Champion!",
                color=0xffd700
            )
            
            await interaction.response.send_message(embed=embed)
            
            # Start battle using PvP system
            await battle_cog.start_battle(
                interaction.channel, interaction.user.id, npc_user_id,
                player_pokemon, npc_pokemon
            )
        
    def _create_npc_pokemon(self, pokemon_data):
        species = POKEMON_DATA[pokemon_data['species_id']]
        level = pokemon_data['level']
        
        # Calculate all stats with proper IVs (10 for NPCs)
        hp = ((species['base_hp'] + 10) * 2 * level // 100) + level + 10
        attack = ((species['base_attack'] + 10) * 2 * level // 100) + 5
        defense = ((species['base_defense'] + 10) * 2 * level // 100) + 5
        special = ((species['base_special'] + 10) * 2 * level // 100) + 5
        speed = ((species['base_speed'] + 10) * 2 * level // 100) + 5
        
        # Get moves from pokemon_data or fallback to basic moves
        moves = pokemon_data.get('moves', ['tackle', 'growl', None, None])
        
        return {
            'id': -1,  # NPC Pokemon
            'species_id': pokemon_data['species_id'],
            'name': species['name'],
            'level': level,
            'current_hp': hp,
            'hp_iv': 10,
            'attack_iv': 10,
            'defense_iv': 10,
            'special_iv': 10,
            'speed_iv': 10,
            'move1': moves[0] if len(moves) > 0 else 'tackle',
            'move2': moves[1] if len(moves) > 1 else 'growl',
            'move3': moves[2] if len(moves) > 2 else None,
            'move4': moves[3] if len(moves) > 3 else None,
            # Add calculated stats for battle system
            'calculated_attack': attack,
            'calculated_defense': defense,
            'calculated_special': special,
            'calculated_speed': speed
        }
        

            

        

        

            
    async def _handle_gym_victory(self, gym_battle_data):
        # Find player ID from battle system
        battle_cog = self.bot.get_cog('Battle')
        player_id = None
        channel = None
        for user_id, battle_data in battle_cog.active_battles.items():
            if user_id > 0:  # Player ID
                player_id = user_id
                channel = battle_data['channel']
                break
                
        if not player_id:
            return
            
        user_id = player_id
        is_rematch = gym_battle_data.get('is_rematch', False)
        
        if gym_battle_data['type'] == 'gym':
            leader_data = GYM_LEADERS[gym_battle_data['leader']]
            reward = leader_data['reward']
            badge_name = leader_data['badge']
            
            if not is_rematch:
                await self.bot.db.execute(
                    "UPDATE users SET badges = badges + 1, money = money + $1 WHERE user_id = $2",
                    reward, user_id
                )
                embed = discord.Embed(
                    title="Victory!",
                    description=f"You defeated {leader_data['name']} and earned the {badge_name}!",
                    color=0x00ff00
                )
                embed.add_field(name="Reward", value=f"{reward:,} rupees", inline=True)
            else:
                embed = discord.Embed(
                    title="Rematch Victory!",
                    description=f"You defeated {leader_data['name']} in a rematch!",
                    color=0x00ff00
                )
                embed.add_field(name="Reward", value="No rewards for rematches", inline=True)
            
        elif gym_battle_data['type'] == 'elite4':
            member_data = ELITE_FOUR[gym_battle_data['member']]
            reward = member_data['reward']
            
            if not is_rematch:
                await self.bot.db.execute(
                    "UPDATE users SET badges = badges + 1, money = money + $1 WHERE user_id = $2",
                    reward, user_id
                )
                embed = discord.Embed(
                    title="Elite Four Victory!",
                    description=f"You defeated {member_data['name']} of the Elite Four!",
                    color=0x9b59b6
                )
                embed.add_field(name="Reward", value=f"{reward:,} rupees", inline=True)
            else:
                embed = discord.Embed(
                    title="Elite Four Rematch Victory!",
                    description=f"You defeated {member_data['name']} in a rematch!",
                    color=0x9b59b6
                )
                embed.add_field(name="Reward", value="No rewards for rematches", inline=True)
            
        else:  # champion
            reward = CHAMPION['blue']['reward']
            
            if not is_rematch:
                await self.bot.db.execute(
                    "UPDATE users SET badges = badges + 1, money = money + $1 WHERE user_id = $2",
                    reward, user_id
                )
                embed = discord.Embed(
                    title="CHAMPION!",
                    description="You are the new Pokemon Champion!",
                    color=0xffd700
                )
                embed.add_field(name="Reward", value=f"{reward:,} rupees", inline=True)
            else:
                embed = discord.Embed(
                    title="Champion Rematch Victory!",
                    description="You defeated the Champion in a rematch!",
                    color=0xffd700
                )
                embed.add_field(name="Reward", value="No rewards for rematches", inline=True)
            
        if channel:
            await channel.send(embed=embed)
        
        # Clean up
        if user_id in self.active_gym_battles:
            del self.active_gym_battles[user_id]
        
    async def _handle_player_loss(self, gym_battle_data):
        # Find player ID from battle system
        battle_cog = self.bot.get_cog('Battle')
        player_id = None
        channel = None
        for user_id, battle_data in battle_cog.active_battles.items():
            if user_id > 0:  # Player ID
                player_id = user_id
                channel = battle_data['channel']
                break
                
        if not player_id:
            return
            
        embed = discord.Embed(
            title="Defeat...",
            description="Your Pokemon fainted! Better luck next time!",
            color=0xe74c3c
        )
        
        if channel:
            await channel.send(embed=embed)
        
        # Clean up
        if player_id in self.active_gym_battles:
            del self.active_gym_battles[player_id]
        
    def _calculate_damage(self, attacker, defender, move_name):
        if move_name not in MOVES_DATA:
            return random.randint(10, 20)
            
        move = MOVES_DATA[move_name]
        if move['power'] == 0:
            return 0
            
        attacker_species = POKEMON_DATA[attacker['species_id']]
        defender_species = POKEMON_DATA[defender['species_id']]
        
        # Gen 1 damage formula
        level = attacker['level']
        
        if move['category'] == 'physical':
            attack = self._calculate_stat(attacker_species['base_attack'], attacker.get('attack_iv', 10), level)
            defense = self._calculate_stat(defender_species['base_defense'], defender.get('defense_iv', 10), defender['level'])
        else:
            attack = self._calculate_stat(attacker_species['base_special'], attacker.get('special_iv', 10), level)
            defense = self._calculate_stat(defender_species['base_special'], defender.get('special_iv', 10), defender['level'])
        
        # Gen 1 formula: ((((2 * Level + 10) / 250) * (Attack / Defense) * Base) + 2) * Modifiers
        damage = (((2 * level + 10) / 250) * (attack / defense) * move['power'] + 2)
        
        # STAB (Same Type Attack Bonus)
        if (move['type'].lower() == attacker_species['type1'].lower() or 
            (attacker_species.get('type2') and move['type'].lower() == attacker_species['type2'].lower())):
            damage *= 1.5
        
        # Type effectiveness
        effectiveness = self._get_move_effectiveness(move_name, defender['species_id'])
        damage *= effectiveness
        
        # Gen 1 random factor (217-255)/255
        random_factor = random.randint(217, 255) / 255
        damage *= random_factor
        
        return max(1, int(damage))
    
    def _get_move_effectiveness(self, move_name, defender_species_id):
        """Calculate type effectiveness for a move against a defender"""
        if move_name not in MOVES_DATA:
            return 1.0
            
        move = MOVES_DATA[move_name]
        defender_species = POKEMON_DATA[defender_species_id]
        
        effectiveness = 1.0
        if move['type'].lower() in TYPE_EFFECTIVENESS:
            if defender_species['type1'].lower() in TYPE_EFFECTIVENESS[move['type'].lower()]:
                effectiveness *= TYPE_EFFECTIVENESS[move['type'].lower()][defender_species['type1'].lower()]
            if defender_species.get('type2') and defender_species['type2'].lower() in TYPE_EFFECTIVENESS[move['type'].lower()]:
                effectiveness *= TYPE_EFFECTIVENESS[move['type'].lower()][defender_species['type2'].lower()]
        
        return effectiveness
        
    def _calculate_stat(self, base_stat, iv, level):
        return int(((base_stat + iv) * 2 * level / 100) + 5)
        
    def _calculate_max_hp(self, pokemon):
        species = POKEMON_DATA[pokemon['species_id']]
        return ((species['base_hp'] + pokemon.get('hp_iv', 10)) * 2 * pokemon['level'] // 100) + pokemon['level'] + 10
        
    def _choose_best_move(self, attacker, defender, moves):
        """Gen 1 AI: Simple effectiveness-based selection"""
        valid_moves = [m for m in moves if m and m in MOVES_DATA]
        if not valid_moves:
            return "tackle"
        
        # Filter out status moves (Gen 1 AI rarely used them)
        damage_moves = [m for m in valid_moves if MOVES_DATA[m]['power'] > 0]
        if not damage_moves:
            return random.choice(valid_moves)
        
        # Find super effective moves
        super_effective = []
        for move_name in damage_moves:
            effectiveness = self._get_move_effectiveness(move_name, defender['species_id'])
            if effectiveness > 1.0:
                super_effective.append(move_name)
        
        # Gen 1 AI: Use super effective move if available, otherwise random
        if super_effective:
            return random.choice(super_effective)
        else:
            return random.choice(damage_moves)
        
    async def _handle_gym_timeout(self, battle_data, user_id):
        """Handle 3-minute gym battle timeout"""
        await asyncio.sleep(180)  # 3 minutes
        
        if user_id in self.active_gym_battles:
            embed = discord.Embed(
                title="Battle Timeout!",
                description="You took too long to make a move. Battle ended.",
                color=0xff0000
            )
            
            await battle_data['channel'].send(embed=embed)
            del self.active_gym_battles[user_id]

class GymMoveView(discord.ui.View):
    def __init__(self, bot, battle_data):
        super().__init__(timeout=180)
        self.bot = bot
        self.battle_data = battle_data
        
        pokemon = battle_data['player']['pokemon']
        moves = [pokemon['move1'], pokemon['move2'], pokemon['move3'], pokemon['move4']]
        
        for i, move in enumerate(moves):
            if move:
                button = discord.ui.Button(label=move.replace('_', ' ').title(), custom_id=f"gym_move_{i}")
                button.callback = self._create_move_callback(move)
                self.add_item(button)
                
        # Add switch Pokemon button - assume user has other Pokemon for now
        # Will be validated when button is clicked
        switch_button = discord.ui.Button(label="Switch Pokemon", style=discord.ButtonStyle.secondary, custom_id="switch")
        switch_button.callback = self._switch_pokemon
        self.add_item(switch_button)
                
    def _create_move_callback(self, move_name):
        async def callback(interaction):
            if interaction.user.id != self.battle_data['player']['id']:
                await interaction.response.send_message("Not your battle!", ephemeral=True)
                return
                
            gym_cog = self.bot.get_cog('Gym')
            result = await gym_cog.use_gym_move(self.battle_data, move_name)
            
            try:
                await interaction.response.send_message(result)
            except discord.HTTPException:
                await self.battle_data['channel'].send(result)
            
            # Handle NPC faint after showing move result
            if self.battle_data.get('npc_fainted'):
                del self.battle_data['npc_fainted']
                await gym_cog._handle_npc_faint(self.battle_data)
            elif self.battle_data['player']['id'] in gym_cog.active_gym_battles:
                await gym_cog._send_gym_battle_status(self.battle_data)
                
        return callback
        
    async def _switch_pokemon(self, interaction):
        if interaction.user.id != self.battle_data['player']['id']:
            await interaction.response.send_message("It's not your turn!", ephemeral=True)
            return
            
        # Show Pokemon selection
        view = GymPokemonSwitchView(self.bot, self.battle_data, interaction.user.id)
        await view.setup_buttons()
        await interaction.response.send_message("Choose a Pokemon to switch to:", view=view, ephemeral=True)

class GymPokemonSwitchView(discord.ui.View):
    def __init__(self, bot, battle_data, user_id):
        super().__init__(timeout=60)
        self.bot = bot
        self.battle_data = battle_data
        self.user_id = user_id
        
    async def setup_buttons(self):
        # Get party and add buttons
        party = await self.bot.db.get_user_pokemon(self.user_id, in_party=True)
        current_pokemon = self.battle_data['player']['pokemon']
        
        for i, pokemon in enumerate(party):
            if pokemon['current_hp'] > 0 and pokemon['id'] != current_pokemon['id']:
                from data.complete_pokemon_data import COMPLETE_POKEMON_DATA
                species = COMPLETE_POKEMON_DATA[pokemon['species_id']]
                button = discord.ui.Button(
                    label=f"{species['name']} (Lv.{pokemon['level']})",
                    custom_id=f"gym_switch_{i}"
                )
                button.callback = self._create_switch_callback(i)
                self.add_item(button)
                
    def _create_switch_callback(self, pokemon_index):
        async def callback(interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("Not your Pokemon!", ephemeral=True)
                return
                
            # Get fresh party data
            party = await self.bot.db.get_user_pokemon(self.user_id, in_party=True)
            new_pokemon = party[pokemon_index]
            
            # Switch Pokemon
            self.battle_data['player']['pokemon'] = dict(new_pokemon)
            
            from data.complete_pokemon_data import COMPLETE_POKEMON_DATA
            species = COMPLETE_POKEMON_DATA[new_pokemon['species_id']]
            
            # Switch turn to NPC
            self.battle_data['turn'] = 'npc'
            await interaction.response.send_message(f"Switched to {species['name']}!")
            
            gym_cog = self.bot.get_cog('Gym')
            await gym_cog._send_gym_battle_status(self.battle_data)
                
        return callback

async def setup(bot):
    await bot.add_cog(Gym(bot))