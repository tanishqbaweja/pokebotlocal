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
        # Find player ID from gym battle data
        player_id = None
        for uid, data in self.active_gym_battles.items():
            if data['npc_user_id'] == gym_battle_data['npc_user_id']:
                player_id = uid
                break

        if not player_id:
            return None

        user_id = player_id
        is_rematch = gym_battle_data.get('is_rematch', False)
        embed = None
        
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
        
        # Clean up
        if user_id in self.active_gym_battles:
            del self.active_gym_battles[user_id]

        return embed
        
    async def _handle_player_loss(self, gym_battle_data):
        # Find player ID from gym battle data
        player_id = None
        for uid, data in self.active_gym_battles.items():
            if data['npc_user_id'] == gym_battle_data['npc_user_id']:
                player_id = uid
                break
                
        if not player_id:
            return None
            
        embed = discord.Embed(
            title="Defeat...",
            description="Your Pokemon fainted! Better luck next time!",
            color=0xe74c3c
        )
        
        # Clean up
        if player_id in self.active_gym_battles:
            del self.active_gym_battles[player_id]
            
        return embed

async def setup(bot):
    await bot.add_cog(Gym(bot))