import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
import logging
import aiohttp
from data.complete_pokemon_data import COMPLETE_POKEMON_DATA as POKEMON_DATA
from data.complete_moves_data import COMPLETE_MOVES_DATA as MOVES_DATA, SECONDARY_EFFECTS
from data.complete_moves_data import TYPE_EFFECTIVENESS

class Battle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_battles = {}  # user_id: battle_data
        
    @app_commands.command(name="battle", description="Challenge another trainer to battle")
    async def battle(self, interaction: discord.Interaction, opponent: discord.Member):
        challenger_id = interaction.user.id
        opponent_id = opponent.id

        # Rate Limiter Check
        rate_limiter = self.bot.get_cog('RateLimiter')
        if rate_limiter and rate_limiter.is_rate_limited(challenger_id, 'battle'):
            cooldown = rate_limiter.get_cooldown_time(challenger_id, 'battle')
            await interaction.response.send_message(f"You're challenging too frequently! Try again in {cooldown:.1f} seconds.", ephemeral=True)
            return
        
        if challenger_id == opponent_id:
            await interaction.response.send_message("You can't battle yourself!", ephemeral=True)
            return
            
        # Check for pending move learning
        move_learning_cog = self.bot.get_cog('MoveLearning')
        if move_learning_cog:
            if move_learning_cog.has_pending_moves(challenger_id):
                await interaction.response.send_message("You have a Pokemon waiting to learn a move! Use `/choosemove` or `/forgetmove` first.", ephemeral=True)
                return
            if move_learning_cog.has_pending_moves(opponent_id):
                await interaction.response.send_message(f"{opponent.mention} has a Pokemon waiting to learn a move and cannot battle right now.", ephemeral=True)
                return
            
        # Check for battles in this server only
        server_id = interaction.guild.id
        challenger_battle = self.active_battles.get(challenger_id)
        opponent_battle = self.active_battles.get(opponent_id)
        
        if (challenger_battle and challenger_battle.get('server_id') == server_id) or \
           (opponent_battle and opponent_battle.get('server_id') == server_id):
            await interaction.response.send_message("One of you is already in battle in this server!", ephemeral=True)
            return
            
        # Check both users have Pokemon
        challenger_party = await self.bot.db.get_user_pokemon(challenger_id, in_party=True)
        opponent_party = await self.bot.db.get_user_pokemon(opponent_id, in_party=True)
        
        challenger_alive = [p for p in challenger_party if p['current_hp'] > 0] if challenger_party else []
        opponent_alive = [p for p in opponent_party if p['current_hp'] > 0] if opponent_party else []
        
        if not challenger_alive or not opponent_alive:
            await interaction.response.send_message("Both trainers need Pokemon with HP > 0 to battle!", ephemeral=True)
            return
            
        # Create battle request
        view = BattleRequestView(self.bot, challenger_id, opponent_id, challenger_alive[0], opponent_alive[0])
        embed = discord.Embed(
            title="Battle Challenge!",
            description=f"{interaction.user.mention} challenges {opponent.mention} to a Pokemon battle!",
            color=0xe74c3c
        )
        
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()
        
    async def start_battle(self, channel, challenger_id, opponent_id, challenger_pokemon, opponent_pokemon):
        # Only store PvP battles in database (both IDs positive)
        if challenger_id > 0 and opponent_id > 0:
            try:
                battle_id = await self.bot.db.fetchval(
                    """INSERT INTO battles (challenger_id, opponent_id, challenger_pokemon, opponent_pokemon, 
                       turn_user_id, battle_data, status) 
                       VALUES ($1, $2, $3, $4, $5, $6, 'active') RETURNING id""",
                    challenger_id, opponent_id, challenger_pokemon['id'], opponent_pokemon['id'],
                    challenger_id, '{}'
                )
            except Exception as e:
                import logging
                logging.warning(f"Failed to store battle in database: {e}")
                battle_id = random.randint(1000, 9999)  # Fallback ID
        else:
            # NPC battle - use fallback ID and check completion status
            battle_id = random.randint(1000, 9999)
            
            # Check if this is first-time completion for NPC battle
            if challenger_id > 0:  # Only for real players
                npc_type = abs(opponent_id) // 1000  # 1=gym, 2=elite4, 3=champion
                npc_index = abs(opponent_id) % 1000
                
                try:
                    # Check existing completion
                    existing = await self.bot.db.fetchval(
                        "SELECT 1 FROM npc_completions WHERE user_id = $1 AND npc_type = $2 AND npc_index = $3",
                        challenger_id, npc_type, npc_index
                    )
                    is_first_completion = existing is None
                except:
                    # Table might not exist, assume first completion
                    is_first_completion = True
        
        # Get full parties
        challenger_party = await self.bot.db.get_user_pokemon(challenger_id, in_party=True)
        opponent_party = await self.bot.db.get_user_pokemon(opponent_id, in_party=True)
        
        battle_data = {
            'id': battle_id,
            'challenger': {'id': challenger_id, 'pokemon': challenger_pokemon, 'party': challenger_party, 'current_index': 0, 'stats': {}},
            'opponent': {'id': opponent_id, 'pokemon': opponent_pokemon, 'party': opponent_party, 'current_index': 0, 'stats': {}},
            'turn': challenger_id,
            'channel': channel,
            'server_id': channel.guild.id
        }
        
        # Add first completion flag for NPC battles
        if challenger_id > 0 and opponent_id < 0:
            battle_data['is_first_completion'] = is_first_completion
        
        # Initialize battle stats and status
        for side in ['challenger', 'opponent']:
            pokemon = battle_data[side]['pokemon']
            battle_data[side]['stats'] = {
                'attack': 0, 'defense': 0, 'special': 0, 'speed': 0,
                'accuracy': 0, 'evasion': 0
            }
            battle_data[side]['status'] = None
            battle_data[side]['status_turns'] = 0
            battle_data[side]['confused'] = False
            battle_data[side]['confusion_turns'] = 0
            battle_data[side]['seeded'] = False
            battle_data[side]['substitute'] = 0
            battle_data[side]['transformed'] = False
            battle_data[side]['focus_energy'] = False
            battle_data[side]['disabled_move'] = None
            battle_data[side]['disable_turns'] = 0
            
        battle_data['turn_start_time'] = asyncio.get_event_loop().time()
        battle_data['turn_timeout_task'] = None
            
        self.active_battles[challenger_id] = battle_data
        self.active_battles[opponent_id] = battle_data
        
        await self._send_battle_status(battle_data)
        
    async def _send_battle_status(self, battle_data):
        challenger_pokemon = battle_data['challenger']['pokemon']
        opponent_pokemon = battle_data['opponent']['pokemon']
        
        embed = discord.Embed(title="Pokemon Battle!", color=0xf39c12)
        
        # Challenger Pokemon with status
        c_max_hp = self._calculate_max_hp(challenger_pokemon)
        c_hp_bar = self._create_hp_bar(challenger_pokemon['current_hp'], c_max_hp)
        c_status_text = self._get_status_display(battle_data['challenger'])
        embed.add_field(
            name=f"{challenger_pokemon['name']} (Lv.{challenger_pokemon['level']})",
            value=f"{c_hp_bar} {challenger_pokemon['current_hp']}/{c_max_hp}\n{c_status_text}",
            inline=True
        )
        
        embed.add_field(name="VS", value="⚔️", inline=True)
        
        # Opponent Pokemon with status
        o_max_hp = self._calculate_max_hp(opponent_pokemon)
        o_hp_bar = self._create_hp_bar(opponent_pokemon['current_hp'], o_max_hp)
        o_status_text = self._get_status_display(battle_data['opponent'])
        embed.add_field(
            name=f"{opponent_pokemon['name']} (Lv.{opponent_pokemon['level']})",
            value=f"{o_hp_bar} {opponent_pokemon['current_hp']}/{o_max_hp}\n{o_status_text}",
            inline=True
        )
        
        # Turn indicator
        current_user = battle_data['turn']
        embed.add_field(
            name="Turn",
            value=f"<@{current_user}>'s turn",
            inline=False
        )
        
        # Check if current user is NPC (negative ID)
        if current_user < 0:
            # NPC turn - make automatic move
            await self._handle_npc_turn(battle_data)
        else:
            # Player turn - show move selection
            view = BattleMoveView(self.bot, battle_data, current_user)
            message = await battle_data['channel'].send(embed=embed, view=view)
            view.message = message
        
        # Set turn timeout
        if battle_data.get('turn_timeout_task'):
            battle_data['turn_timeout_task'].cancel()
        battle_data['turn_timeout_task'] = asyncio.create_task(self._handle_turn_timeout(battle_data, current_user))
        battle_data['turn_start_time'] = asyncio.get_event_loop().time()
        
    async def use_move(self, battle_data, user_id, move_name):
        return_data = {'text': '', 'end_embed': None}

        if battle_data['turn'] != user_id:
            return_data['text'] = "It's not your turn!"
            return return_data
            
        # Cancel timeout task
        if battle_data.get('turn_timeout_task'):
            battle_data['turn_timeout_task'].cancel()
            
        # Determine attacker and defender
        if user_id == battle_data['challenger']['id']:
            attacker_data = battle_data['challenger']
            defender_data = battle_data['opponent']
        else:
            attacker_data = battle_data['opponent']
            defender_data = battle_data['challenger']
            
        # Check if Pokemon can move (status effects)
        status_cog = self.bot.get_cog('StatusEffects')
        if status_cog:
            can_move, status_message = status_cog.can_use_move(attacker_data)
            if not can_move:
                result_text = status_message
                battle_data['turn'] = defender_data['id']
                return_data['text'] = result_text
                return return_data
            
        move = MOVES_DATA.get(move_name)
        if not move:
            return_data['text'] = "Invalid move!"
            return return_data
            
        result_text = f"{attacker_data['pokemon']['name']} used {move_name.replace('_', ' ').title()}!\n"
        
        # Check move accuracy first (only for non-status moves)
        if move['category'] != 'status' and not self._check_move_accuracy(move, attacker_data, defender_data):
            result_text += "The attack missed!"
            battle_data['turn'] = defender_data['id']
            return_data['text'] = result_text
            return return_data
        
        # Handle status moves
        if move['category'] == 'status':
            status_result = await self._handle_status_move(battle_data, attacker_data, defender_data, move_name)
            result_text += status_result
            
            # Store last move used for Disable/Mimic
            attacker_data['pokemon'] = dict(attacker_data['pokemon'])
            attacker_data['pokemon']['last_move_used'] = move_name
            
            # Check if status move caused fainting (like Selfdestruct used as status)
            if defender_data['pokemon']['current_hp'] <= 0:
                result_text += f"\n{defender_data['pokemon']['name']} fainted!"
                
                # Award experience for defeating opponent Pokemon
                exp_gained = self._calculate_exp_gain(attacker_data, defender_data)
                if exp_gained > 0:
                    experience_cog = self.bot.get_cog('Experience')
                    if experience_cog:
                        leveled_up = await experience_cog._add_experience(attacker_data['pokemon'], exp_gained)
                        result_text += f"\n{attacker_data['pokemon']['name']} gained {exp_gained} experience!"
                        if leveled_up:
                            result_text += f"\n{attacker_data['pokemon']['name']} grew to level {leveled_up}!"
        else:
            # Calculate damage for attacking moves
            damage = self._calculate_damage(attacker_data, defender_data, move_name)
            
            # Calculate new HP and update database (only for real Pokemon, not NPCs)
            new_hp = max(0, defender_data['pokemon']['current_hp'] - damage)
            if defender_data['pokemon']['id'] > 0:  # Only update database for real Pokemon
                await self.bot.db.execute(
                    "UPDATE pokemon SET current_hp = $1 WHERE id = $2",
                    new_hp, defender_data['pokemon']['id']
                )
            
            # Update battle data with new HP
            defender_data['pokemon'] = dict(defender_data['pokemon'])
            defender_data['pokemon']['current_hp'] = new_hp
            
            # Get effectiveness for message
            effectiveness = self._get_type_effectiveness(move, defender_data['pokemon'])
            
            if damage > 0:
                result_text += f"It dealt {damage} damage!"
                if effectiveness >= 4:
                    result_text += "\nIt's incredibly effective!"
                elif effectiveness >= 2:
                    result_text += "\nIt's super effective!"
                elif effectiveness <= 0.25:
                    result_text += "\nIt's barely effective!"
                elif effectiveness <= 0.5:
                    result_text += "\nIt's not very effective..."
            elif effectiveness == 0:
                result_text += f"\n{defender_data['pokemon']['name']} is immune to that attack!"
            else:
                result_text += "\nIt had no effect!"
                
            # Check for secondary effects on attacking moves
            secondary_effect = self._check_secondary_effects(move_name, defender_data)
            if secondary_effect:
                result_text += f"\n{secondary_effect}"
                
            # Store last move used for Disable/Mimic
            attacker_data['pokemon'] = dict(attacker_data['pokemon'])
            attacker_data['pokemon']['last_move_used'] = move_name
                
            # Check if Pokemon fainted
            if defender_data['pokemon']['current_hp'] <= 0:
                result_text += f"\n{defender_data['pokemon']['name']} fainted!"
                
                # Award experience for defeating opponent Pokemon
                exp_gained = self._calculate_exp_gain(attacker_data, defender_data)
                if exp_gained > 0:
                    experience_cog = self.bot.get_cog('Experience')
                    if experience_cog:
                        leveled_up = await experience_cog._add_experience(attacker_data['pokemon'], exp_gained)
                        result_text += f"\n{attacker_data['pokemon']['name']} gained {exp_gained} experience!"
                        if leveled_up:
                            result_text += f"\n{attacker_data['pokemon']['name']} grew to level {leveled_up}!"
                
                # Handle Pokemon switching (NPC or Player)
                if defender_data['id'] < 0:
                    # NPC Pokemon fainted - get next from gym team
                    gym_cog = self.bot.get_cog('Gym')
                    player_id = attacker_data['id']
                    if gym_cog and player_id in gym_cog.active_gym_battles:
                        gym_battle = gym_cog.active_gym_battles[player_id]
                        gym_battle['npc_team_index'] += 1
                        
                        if gym_battle['npc_team_index'] < len(gym_battle['npc_team']):
                            # Create next NPC Pokemon
                            next_npc_data = gym_battle['npc_team'][gym_battle['npc_team_index']]
                            next_pokemon = gym_cog._create_npc_pokemon(next_npc_data)
                            defender_data['pokemon'] = dict(next_pokemon)
                            
                            # Reset volatile stats for the new NPC Pokemon
                            self._reset_volatile_stats(defender_data)
                            
                            result_text += f"\nEnemy sent out {next_pokemon['name']}!"
                            battle_data['turn'] = defender_data['id']  # NPC's turn with new Pokemon
                            return_data['text'] = result_text
                            return return_data
                        else:
                            # No more NPC Pokemon - player wins, end battle immediately
                            result_text += "\nYou won the battle!"
                            battle_data['turn'] = None  # Clear turn to stop battle
                            end_embed = await self._end_battle(battle_data, attacker_data['id'])
                            return_data['text'] = result_text
                            return_data['end_embed'] = end_embed
                            return return_data
                    else:
                        # No gym battle data found - end battle
                        await self._end_battle(battle_data, attacker_data['id'])
                        return_data['text'] = result_text
                        return return_data
                else:
                    # Player Pokemon fainted - get fresh party data
                    fresh_party = await self.bot.db.get_user_pokemon(defender_data['id'], in_party=True)
                    available_pokemon = [p for p in fresh_party if p['current_hp'] > 0]
                    
                    if len(available_pokemon) == 0:  # No Pokemon left
                        end_embed = await self._end_battle(battle_data, attacker_data['id'])
                        return_data['text'] = result_text
                        return_data['end_embed'] = end_embed
                        return return_data
                    else:
                        # Auto-send next available Pokemon
                        next_pokemon = available_pokemon[0]
                        defender_data['pokemon'] = dict(next_pokemon)
                        defender_data['party'] = fresh_party  # Update cached party
                        for i, p in enumerate(fresh_party):
                            if p['id'] == next_pokemon['id']:
                                defender_data['current_index'] = i
                                break
                        # Reset volatile stats for the new Pokemon
                        self._reset_volatile_stats(defender_data)
                        
                        result_text += f"\n<@{defender_data['id']}> sent out {next_pokemon['name']}!"
                        # Keep turn with same player when Pokemon faints (forced switch)
                        return_data['text'] = result_text
                        return return_data
            
        # Apply end-of-turn status effects
        if status_cog:
            # Apply to attacker
            attacker_status_result = status_cog.apply_status_damage(attacker_data, battle_data)
            if attacker_status_result:
                result_text += f"\n{attacker_status_result}"
                # Update database if HP changed (only for real Pokemon)
                if attacker_data['pokemon']['id'] > 0:
                    await self.bot.db.execute(
                        "UPDATE pokemon SET current_hp = $1 WHERE id = $2",
                        attacker_data['pokemon']['current_hp'], attacker_data['pokemon']['id']
                    )
                
            # Apply to defender
            defender_status_result = status_cog.apply_status_damage(defender_data, battle_data)
            if defender_status_result:
                result_text += f"\n{defender_status_result}"
                # Update database if HP changed (only for real Pokemon)
                if defender_data['pokemon']['id'] > 0:
                    await self.bot.db.execute(
                        "UPDATE pokemon SET current_hp = $1 WHERE id = $2",
                        defender_data['pokemon']['current_hp'], defender_data['pokemon']['id']
                    )
                
        # Switch turns (only if no Pokemon fainted)
        if defender_data['pokemon']['current_hp'] > 0:
            battle_data['turn'] = defender_data['id']

        return_data['text'] = result_text
        return return_data
        
    async def _handle_status_move(self, battle_data, attacker_data, defender_data, move_name):
        """Handle status moves and their effects"""
        attacker = attacker_data['pokemon']
        defender = defender_data['pokemon']
        
        # Stat modification moves
        if move_name in ['growl', 'tail_whip', 'leer']:
            if defender_data.get('mist'):
                return f"{defender['name']} is protected by Mist!"
            if defender_data['stats']['attack'] > -6:
                defender_data['stats']['attack'] -= 1
                return f"{defender['name']}'s Attack fell!"
            return f"{defender['name']}'s Attack won't go any lower!"
            
        elif move_name == 'screech':
            if defender_data.get('mist'):
                return f"{defender['name']} is protected by Mist!"
            if defender_data['stats']['defense'] > -6:
                defender_data['stats']['defense'] = max(-6, defender_data['stats']['defense'] - 2)
                return f"{defender['name']}'s Defense harshly fell!"
            return f"{defender['name']}'s Defense won't go any lower!"
            
        elif move_name in ['sand_attack', 'smokescreen', 'flash', 'kinesis']:
            if defender_data.get('mist'):
                return f"{defender['name']} is protected by Mist!"
            if defender_data['stats']['accuracy'] > -6:
                defender_data['stats']['accuracy'] -= 1
                return f"{defender['name']}'s accuracy fell!"
            return f"{defender['name']}'s accuracy won't go any lower!"
            
        elif move_name in ['swords_dance', 'sharpen', 'meditate']:
            if attacker_data['stats']['attack'] < 6:
                attacker_data['stats']['attack'] += 2 if move_name == 'swords_dance' else 1
                return f"{attacker['name']}'s Attack rose!"
            return f"{attacker['name']}'s Attack won't go any higher!"
            
        elif move_name in ['harden', 'withdraw', 'defense_curl', 'acid_armor']:
            boost = 2 if move_name == 'acid_armor' else 1
            if attacker_data['stats']['defense'] < 6:
                attacker_data['stats']['defense'] += boost
                return f"{attacker['name']}'s Defense rose!"
            return f"{attacker['name']}'s Defense won't go any higher!"
            
        elif move_name in ['agility', 'string_shot']:
            if move_name == 'agility':
                if attacker_data['stats']['speed'] < 6:
                    attacker_data['stats']['speed'] += 2
                    return f"{attacker['name']}'s Speed rose sharply!"
                return f"{attacker['name']}'s Speed won't go any higher!"
            else:  # string_shot
                if defender_data.get('mist'):
                    return f"{defender['name']} is protected by Mist!"
                if defender_data['stats']['speed'] > -6:
                    defender_data['stats']['speed'] -= 1
                    return f"{defender['name']}'s Speed fell!"
                return f"{defender['name']}'s Speed won't go any lower!"
                
        elif move_name == 'barrier':
            if attacker_data['stats']['defense'] < 6:
                attacker_data['stats']['defense'] = min(6, attacker_data['stats']['defense'] + 2)
                return f"{attacker['name']}'s Defense rose sharply!"
            return f"{attacker['name']}'s Defense won't go any higher!"

        elif move_name == 'amnesia':
            if attacker_data['stats']['special'] < 6:
                attacker_data['stats']['special'] = min(6, attacker_data['stats']['special'] + 2)
                return f"{attacker['name']}'s Special rose sharply!"
            return f"{attacker['name']}'s Special won't go any higher!"
            
        elif move_name in ['growth']:
            if attacker_data['stats']['special'] < 6:
                attacker_data['stats']['special'] += 1
                return f"{attacker['name']}'s Special rose!"
            return f"{attacker['name']}'s Special won't go any higher!"
            
        # Status condition moves
        elif move_name in ['poison_powder', 'poison_gas', 'toxic']:
            if defender_data.get('status') is None:
                defender_data['status'] = 'poison'
                return f"{defender['name']} was poisoned!"
            return f"{defender['name']} is already affected by a status condition!"
            
        elif move_name in ['sleep_powder', 'spore', 'sing', 'hypnosis', 'lovely_kiss']:
            if defender_data.get('status') is None:
                defender_data['status'] = 'sleep'
                defender_data['status_turns'] = random.randint(1, 7)
                return f"{defender['name']} fell asleep!"
            return f"{defender['name']} is already affected by a status condition!"
            
        elif move_name in ['stun_spore', 'thunder_wave', 'glare']:
            if defender_data.get('status') is None:
                defender_data['status'] = 'paralysis'
                return f"{defender['name']} was paralyzed!"
            return f"{defender['name']} is already affected by a status condition!"
            
        elif move_name == 'supersonic' or move_name == 'confuse_ray':
            defender_data['confused'] = True
            defender_data['confusion_turns'] = random.randint(2, 5)
            return f"{defender['name']} became confused!"
            
        # Healing moves
        elif move_name in ['recover', 'rest', 'soft_boiled']:
            max_hp = self._calculate_max_hp(attacker)
            if move_name == 'rest':
                heal_amount = max_hp - attacker['current_hp']
                attacker['current_hp'] = max_hp
                attacker_data['status'] = 'sleep'
                attacker_data['status_turns'] = 2
                await self.bot.db.execute(
                    "UPDATE pokemon SET current_hp = $1 WHERE id = $2",
                    max_hp, attacker['id']
                )
                return f"{attacker['name']} went to sleep and recovered all HP!"
            else:
                heal_amount = max_hp // 2
                new_hp = min(max_hp, attacker['current_hp'] + heal_amount)
                attacker['current_hp'] = new_hp
                await self.bot.db.execute(
                    "UPDATE pokemon SET current_hp = $1 WHERE id = $2",
                    new_hp, attacker['id']
                )
                return f"{attacker['name']} recovered {heal_amount} HP!"
                
        # Transform (Ditto's signature move)
        elif move_name == 'transform':
            # Gen 1: Copy opponent's stats, types, moves, and current HP
            defender_species = POKEMON_DATA[defender['species_id']]
            
            # Transform attacker into defender
            attacker_data['transformed'] = True
            attacker_data['original_species'] = attacker['species_id']
            attacker['species_id'] = defender['species_id']
            attacker['name'] = defender['name']
            
            # Copy moves
            attacker['move1'] = defender.get('move1')
            attacker['move2'] = defender.get('move2')
            attacker['move3'] = defender.get('move3')
            attacker['move4'] = defender.get('move4')
            
            # Copy IVs for stat calculation and current HP
            attacker['hp_iv'] = defender['hp_iv']
            attacker['attack_iv'] = defender['attack_iv']
            attacker['defense_iv'] = defender['defense_iv']
            attacker['special_iv'] = defender['special_iv']
            attacker['speed_iv'] = defender['speed_iv']
            attacker['current_hp'] = defender['current_hp']
            
            # Reset stat stages to match opponent
            attacker_data['stats'] = dict(defender_data['stats'])
            
            return f"{attacker['name']} transformed into {defender['name']}!"
            
        # Fixed damage moves
        elif move_name == 'sonic_boom':
            damage = 20
            defender['current_hp'] = max(0, defender['current_hp'] - damage)
            if defender['id'] > 0:  # Only update database for real Pokemon
                await self.bot.db.execute(
                    "UPDATE pokemon SET current_hp = $1 WHERE id = $2",
                    defender['current_hp'], defender['id']
                )
            return f"{defender['name']} took {damage} damage from Sonic Boom!"
            
        elif move_name == 'dragon_rage':
            defender['current_hp'] = max(0, defender['current_hp'] - 40)
            await self.bot.db.execute(
                "UPDATE pokemon SET current_hp = $1 WHERE id = $2",
                defender['current_hp'], defender['id']
            )
            return f"{defender['name']} took 40 damage from Dragon Rage!"
            
        elif move_name == 'night_shade':
            damage = attacker['level']
            defender['current_hp'] = max(0, defender['current_hp'] - damage)
            await self.bot.db.execute(
                "UPDATE pokemon SET current_hp = $1 WHERE id = $2",
                defender['current_hp'], defender['id']
            )
            return f"{defender['name']} took {damage} damage from Night Shade!"
            
        elif move_name == 'seismic_toss':
            damage = attacker['level']
            defender['current_hp'] = max(0, defender['current_hp'] - damage)
            await self.bot.db.execute(
                "UPDATE pokemon SET current_hp = $1 WHERE id = $2",
                defender['current_hp'], defender['id']
            )
            return f"{defender['name']} took {damage} damage from Seismic Toss!"
            
        elif move_name == 'super_fang':
            damage = max(1, defender['current_hp'] // 2)
            defender['current_hp'] = max(0, defender['current_hp'] - damage)
            await self.bot.db.execute(
                "UPDATE pokemon SET current_hp = $1 WHERE id = $2",
                defender['current_hp'], defender['id']
            )
            return f"{defender['name']} took {damage} damage from Super Fang!"
            
        elif move_name == 'psywave':
            damage = random.randint(1, int(attacker['level'] * 1.5))
            defender['current_hp'] = max(0, defender['current_hp'] - damage)
            await self.bot.db.execute(
                "UPDATE pokemon SET current_hp = $1 WHERE id = $2",
                defender['current_hp'], defender['id']
            )
            return f"{defender['name']} took {damage} damage from Psywave!"
            
        # Other status moves
        elif move_name in ['double_team', 'minimize']:
            if attacker_data['stats']['evasion'] < 6:
                attacker_data['stats']['evasion'] += 1
                return f"{attacker['name']}'s evasiveness rose!"
            return f"{attacker['name']}'s evasiveness won't go any higher!"
            
        elif move_name == 'haze':
            # Gen 1: Reset all stat changes and status conditions for both Pokemon
            for side in [attacker_data, defender_data]:
                side['stats'] = {'attack': 0, 'defense': 0, 'special': 0, 'speed': 0, 'accuracy': 0, 'evasion': 0}
                side['status'] = None
                side['status_turns'] = 0
                side['confused'] = False
                side['confusion_turns'] = 0
                # Haze also removes Leech Seed from the user, here we remove from both for simplicity
                side['seeded'] = False
            return "A haze enveloped the battlefield, eliminating all stat changes and status effects!"

        elif move_name == 'mist':
            attacker_data['mist'] = True
            return f"{attacker['name']} is protected by Mist!"

        elif move_name == 'reflect':
            attacker_data['reflect'] = True
            return f"{attacker['name']} raised its Defense with Reflect!"

        elif move_name == 'light_screen':
            attacker_data['light_screen'] = True
            return f"{attacker['name']} raised its Special with Light Screen!"
            
        elif move_name == 'leech_seed':
            if not defender_data.get('seeded'):
                defender_data['seeded'] = True
                return f"{defender['name']} was seeded!"
            return f"{defender['name']} is already seeded!"
            
        elif move_name == 'substitute':
            max_hp = self._calculate_max_hp(attacker)
            cost = max_hp // 4
            if attacker['current_hp'] > cost and not attacker_data.get('substitute'):
                attacker['current_hp'] -= cost
                attacker_data['substitute'] = cost
                await self.bot.db.execute(
                    "UPDATE pokemon SET current_hp = $1 WHERE id = $2",
                    attacker['current_hp'], attacker['id']
                )
                return f"{attacker['name']} created a substitute!"
            return "Not enough HP to create a substitute!"
            
        elif move_name in ['teleport', 'whirlwind', 'roar']:
            return f"{attacker['name']} used {move_name.replace('_', ' ').title()}, but nothing happened!"
            
        elif move_name == 'splash':
            return f"{attacker['name']} splashed around, but nothing happened!"
            
        elif move_name == 'disable':
            # Disable last used move (simplified implementation)
            defender_data['disabled_move'] = defender.get('last_move_used')
            defender_data['disable_turns'] = random.randint(1, 8)
            return f"{defender['name']}'s last move was disabled!"
            
        elif move_name == 'focus_energy':
            attacker_data['focus_energy'] = True
            return f"{attacker['name']} is getting pumped!"
            
        elif move_name == 'conversion':
            # Change type to match first move (simplified)
            if attacker['move1']:
                from data.complete_moves_data import COMPLETE_MOVES_DATA
                move_data = COMPLETE_MOVES_DATA.get(attacker['move1'])
                if move_data:
                    attacker_data['converted_type'] = move_data['type']
                    return f"{attacker['name']} changed type to {move_data['type']}!"
            return f"{attacker['name']} used Conversion, but nothing happened!"
            
        elif move_name == 'mimic':
            # Copy opponent's last used move (simplified)
            if defender.get('last_move_used'):
                attacker_data['mimic_move'] = defender['last_move_used']
                return f"{attacker['name']} learned {defender['last_move_used'].replace('_', ' ').title()}!"
            return f"{attacker['name']} used Mimic, but there was no move to copy!"
            
        return "The move had no effect!"
        
    def _get_type_effectiveness(self, move, defender_pokemon):
        """Calculate type effectiveness multiplier"""
        effectiveness = 1.0
        defender_species = POKEMON_DATA[defender_pokemon['species_id']]
        
        if move['type'].lower() in TYPE_EFFECTIVENESS:
            if defender_species['type1'].lower() in TYPE_EFFECTIVENESS[move['type'].lower()]:
                effectiveness *= TYPE_EFFECTIVENESS[move['type'].lower()][defender_species['type1'].lower()]
            if defender_species.get('type2') and defender_species['type2'].lower() in TYPE_EFFECTIVENESS[move['type'].lower()]:
                effectiveness *= TYPE_EFFECTIVENESS[move['type'].lower()][defender_species['type2'].lower()]
                
        return effectiveness

    def _calculate_damage(self, attacker_data, defender_data, move_name):
        if move_name not in MOVES_DATA:
            return 0
            
        move = MOVES_DATA[move_name]
        
        # Handle special damage moves
        if move_name in ['sonic_boom', 'dragon_rage', 'night_shade', 'seismic_toss', 'super_fang', 'psywave']:
            return 0  # These are handled in status move function
            
        if move['power'] == 0:  # Status moves don't deal damage
            return 0
            
        attacker = attacker_data['pokemon']
        defender = defender_data['pokemon']
        
        # Get Pokemon data
        attacker_species = POKEMON_DATA[attacker['species_id']]
        defender_species = POKEMON_DATA[defender['species_id']]
        
        # Calculate base stats
        if move['category'] == 'physical':
            base_attack = self._calculate_stat(attacker_species['base_attack'], attacker['attack_iv'], attacker['level'])
            base_defense = self._calculate_stat(defender_species['base_defense'], defender['defense_iv'], defender['level'])
            # Apply stat stages
            attack_stat = self._apply_stat_stage(base_attack, attacker_data['stats']['attack'])
            defense_stat = self._apply_stat_stage(base_defense, defender_data['stats']['defense'])
            # Burn halves physical attack in Gen 1
            if attacker_data.get('status') == 'burn':
                attack_stat //= 2
            # Reflect doubles defense vs physical
            if defender_data.get('reflect'):
                defense_stat *= 2
        else:
            base_special_att = self._calculate_stat(attacker_species['base_special'], attacker['special_iv'], attacker['level'])
            base_special_def = self._calculate_stat(defender_species['base_special'], defender['special_iv'], defender['level'])
            attack_stat = self._apply_stat_stage(base_special_att, attacker_data['stats']['special'])
            defense_stat = self._apply_stat_stage(base_special_def, defender_data['stats']['special'])
            # Light Screen doubles special vs special
            if defender_data.get('light_screen'):
                defense_stat *= 2
            
        # Base damage calculation
        damage = ((2 * attacker['level'] + 10) / 250) * (attack_stat / defense_stat) * move['power'] + 2
        
        # Type effectiveness
        effectiveness = self._get_type_effectiveness(move, defender)
                
        # STAB (Same Type Attack Bonus)
        if move['type'].lower() == attacker_species['type1'].lower() or (attacker_species.get('type2') and move['type'].lower() == attacker_species['type2'].lower()):
            effectiveness *= 1.5
            
        # Critical hit calculation
        crit_chance = 16  # Base 6.25% (1/16)
        high_crit_moves = ['slash', 'razor_leaf', 'crabhammer', 'karate_chop']
        if move_name in high_crit_moves:
            crit_chance = 8  # 12.5% (1/8)

        # Gen 1 Focus Energy bug: it quarters the crit rate instead of doubling it
        if attacker_data.get('focus_energy'):
            crit_chance *= 4
            
        if random.randint(1, crit_chance) == 1:
            effectiveness *= 2
            result_text += "\nA critical hit!"
            
        # Random factor (85-100%)
        random_factor = random.randint(85, 100) / 100
        
        return int(damage * effectiveness * random_factor)
        
    def _get_status_display(self, pokemon_data):
        """Get status and stat changes display for battle UI"""
        status_parts = []
        
        # Status condition
        if pokemon_data.get('status'):
            status_icons = {
                'poison': '🟣 PSN', 'burn': '🔥 BRN', 'paralysis': '⚡ PAR',
                'sleep': '💤 SLP', 'freeze': '🧊 FRZ'
            }
            status_parts.append(status_icons.get(pokemon_data['status'], pokemon_data['status'].upper()))
            
        # Confusion
        if pokemon_data.get('confused'):
            status_parts.append('😵 CNF')
            
        # Stat changes
        stats = pokemon_data.get('stats', {})
        stat_changes = []
        for stat, value in stats.items():
            if value != 0:
                sign = '+' if value > 0 else ''
                stat_changes.append(f"{stat.upper()}{sign}{value}")
                
        if stat_changes:
            status_parts.append(' '.join(stat_changes))
            
        # Other effects
        if pokemon_data.get('seeded'):
            status_parts.append('🌱 SEED')
        if pokemon_data.get('substitute'):
            status_parts.append('🪆 SUB')
        if pokemon_data.get('transformed'):
            status_parts.append('🔄 TFRM')
            
        return ' | '.join(status_parts) if status_parts else 'No effects'

    def _create_hp_bar(self, current_hp, max_hp):
        """Creates a text-based HP bar."""
        hp_percentage = current_hp / max_hp
        bar_length = 10
        filled_length = int(bar_length * hp_percentage)

        if hp_percentage > 0.5:
            color = '🟩'
        elif hp_percentage > 0.2:
            color = '🟨'
        else:
            color = '🟥'

        bar = color * filled_length + '⬜' * (bar_length - filled_length)
        return f"[{bar}]"
        
    def _check_secondary_effects(self, move_name, defender_data):
        """Check for secondary effects of attacking moves using SECONDARY_EFFECTS data"""
        if move_name not in SECONDARY_EFFECTS:
            return None
            
        effect_data = SECONDARY_EFFECTS[move_name]
        if random.randint(1, 100) > effect_data['chance']:
            return None
            
        defender = defender_data['pokemon']
        effect = effect_data['effect']
        
        if effect == 'paralysis':
            if defender_data.get('status') is None:
                defender_data['status'] = 'paralysis'
                return f"{defender['name']} was paralyzed!"
        elif effect == 'freeze':
            if defender_data.get('status') is None:
                defender_data['status'] = 'freeze'
                return f"{defender['name']} was frozen!"
        elif effect == 'burn':
            if defender_data.get('status') is None:
                defender_data['status'] = 'burn'
                return f"{defender['name']} was burned!"
        elif effect == 'poison':
            if defender_data.get('status') is None:
                defender_data['status'] = 'poison'
                return f"{defender['name']} was poisoned!"
        elif effect == 'confusion':
            defender_data['confused'] = True
            defender_data['confusion_turns'] = random.randint(2, 5)
            return f"{defender['name']} became confused!"
        elif effect == 'speed_down':
            if defender_data['stats']['speed'] > -6:
                defender_data['stats']['speed'] -= 1
                return f"{defender['name']}'s Speed fell!"
        elif effect == 'attack_down':
            if defender_data['stats']['attack'] > -6:
                defender_data['stats']['attack'] -= 1
                return f"{defender['name']}'s Attack fell!"
        elif effect == 'defense_down':
            if defender_data['stats']['defense'] > -6:
                defender_data['stats']['defense'] -= 1
                return f"{defender['name']}'s Defense fell!"
        elif effect == 'flinch':
            # Flinch only works if the move goes first (simplified implementation)
            return f"{defender['name']} flinched!"
            
        return None
        
    def _check_move_accuracy(self, move, attacker_data, defender_data):
        """Check if move hits based on accuracy and evasion"""
        base_accuracy = move['accuracy']
        
        # Apply accuracy and evasion stat modifications
        accuracy_stage = attacker_data['stats'].get('accuracy', 0)
        evasion_stage = defender_data['stats'].get('evasion', 0)
        
        # Calculate stage multiplier
        net_stage = accuracy_stage - evasion_stage
        if net_stage >= 0:
            stage_multiplier = (3 + net_stage) / 3
        else:
            stage_multiplier = 3 / (3 - net_stage)
            
        final_accuracy = min(100, base_accuracy * stage_multiplier)
        
        return random.randint(1, 100) <= final_accuracy
        
    def _apply_stat_stage(self, base_stat, stage):
        """Apply stat stage modifications (-6 to +6)"""
        if stage == 0:
            return base_stat
        elif stage > 0:
            return int(base_stat * (2 + stage) / 2)
        else:
            return int(base_stat * 2 / (2 - stage))
            
    async def _handle_turn_timeout(self, battle_data, user_id):
        """Handle 3-minute turn timeout"""
        await asyncio.sleep(180)  # 3 minutes
        
        if user_id in self.active_battles:
            # Auto-forfeit on timeout
            other_user = battle_data['challenger']['id'] if user_id == battle_data['opponent']['id'] else battle_data['opponent']['id']
            
            # Get proper name for NPC
            if other_user < 0:
                gym_cog = self.bot.get_cog('Gym')
                player_id = user_id if user_id > 0 else (battle_data['challenger']['id'] if battle_data['challenger']['id'] > 0 else battle_data['opponent']['id'])
                if gym_cog and player_id in gym_cog.active_gym_battles:
                    gym_battle = gym_cog.active_gym_battles[player_id]
                    if gym_battle['type'] == 'gym':
                        from data.gym_data import GYM_LEADERS
                        npc_name = GYM_LEADERS[gym_battle['leader']]['name']
                    elif gym_battle['type'] == 'elite4':
                        from data.gym_data import ELITE_FOUR
                        npc_name = ELITE_FOUR[gym_battle['member']]['name']
                    else:
                        from data.gym_data import CHAMPION
                        npc_name = CHAMPION['blue']['name']
                    other_display = npc_name
                else:
                    other_display = "NPC"
            else:
                other_display = f"<@{other_user}>"
            
            embed = discord.Embed(
                title="Battle Timeout!",
                description=f"<@{user_id}> took too long to move. {other_display} wins by forfeit!",
                color=0xff0000
            )
            
            await battle_data['channel'].send(embed=embed)
            end_embed = await self._end_battle(battle_data, other_user)
            if end_embed:
                await asyncio.sleep(0.1)
                await battle_data['channel'].send(embed=end_embed)
        
    def _calculate_stat(self, base_stat, iv, level):
        return int(((base_stat + iv) * 2 * level / 100) + 5)
        
    def _calculate_max_hp(self, pokemon):
        species = POKEMON_DATA[pokemon['species_id']]
        return ((species['base_hp'] + pokemon['hp_iv']) * 2 * pokemon['level'] // 100) + pokemon['level'] + 10

    def _calculate_exp_gain(self, attacker_data, defender_data):
        """Calculates experience points gained from defeating a Pokemon based on Gen 1 formula."""
        if attacker_data['pokemon']['id'] <= 0:  # Don't award exp to NPCs
            return 0

        defender_pokemon = defender_data['pokemon']
        defender_species = POKEMON_DATA[defender_pokemon['species_id']]

        base_exp = defender_species.get('base_experience', 60)  # Fallback for safety
        level = defender_pokemon['level']

        # All battles are trainer battles in this bot (PvP or PvE vs Gym/Elite4)
        trainer_battle_multiplier = 1.5

        exp_gained = int((trainer_battle_multiplier * base_exp * level) / 7)

        return exp_gained

    def _reset_volatile_stats(self, side_data):
        """Resets stats and conditions that are cleared on switch."""
        side_data['stats'] = {
            'attack': 0, 'defense': 0, 'special': 0, 'speed': 0,
            'accuracy': 0, 'evasion': 0
        }
        side_data['confused'] = False
        side_data['confusion_turns'] = 0
        side_data['seeded'] = False
        side_data['substitute'] = 0
        side_data['transformed'] = False
        side_data['focus_energy'] = False
        side_data['disabled_move'] = None
        side_data['disable_turns'] = 0
        side_data['reflect'] = False
        side_data['light_screen'] = False
        side_data['mist'] = False
        
    def _choose_strategic_move(self, npc_data, battle_data, valid_moves):
        """Enhanced strategic AI for NPC move selection"""
        player_data = battle_data['challenger'] if battle_data['challenger']['id'] > 0 else battle_data['opponent']
        player_pokemon = player_data['pokemon']
        npc_pokemon = npc_data['pokemon']
        
        move_scores = []
        
        for move_name in valid_moves:
            move = MOVES_DATA[move_name]
            score = 0
            
            # Base score for damage moves
            if move['power'] > 0:
                score += move['power']
                
                # Type effectiveness bonus
                effectiveness = self._get_type_effectiveness(move, player_pokemon)
                if effectiveness >= 2:
                    score += 60  # Super effective
                elif effectiveness <= 0.5:
                    score -= 40  # Not very effective
                elif effectiveness == 0:
                    score = 0  # No effect
                    
                # Priority for high-damage moves when opponent is low HP
                player_hp_percent = player_pokemon['current_hp'] / self._calculate_max_hp(player_pokemon)
                if player_hp_percent < 0.3 and move['power'] >= 80:
                    score += 40  # Go for the KO
                    
                # Avoid weak moves when opponent has high HP
                if player_hp_percent > 0.8 and move['power'] < 40:
                    score -= 20
                    
            # Enhanced status move strategy
            elif move['category'] == 'status':
                player_stats = player_data.get('stats', {})
                npc_stats = npc_data.get('stats', {})

                # Defensive reaction to player's high stats
                if player_stats.get('attack', 0) >= 2:
                    if move_name in ['reflect', 'harden', 'withdraw']:
                        score += 30 # Prioritize physical defense
                    if move_name in ['growl', 'tail_whip']:
                        score += 30 # Prioritize lowering player's attack

                if player_stats.get('special', 0) >= 2:
                    if move_name == 'light_screen':
                        score += 30 # Prioritize special defense

                    # Healing moves when low HP
                    if move_name in ['recover', 'rest', 'soft_boiled']:
                        npc_hp_percent = npc_pokemon['current_hp'] / self._calculate_max_hp(npc_pokemon)
                        if npc_hp_percent < 0.25:
                            score = 90  # Critical healing
                        elif npc_hp_percent < 0.5:
                            score = 50
                        else:
                            score = 10  # Don't heal when healthy

                    # Stat boosting when healthy and no status effects
                    elif move_name in ['swords_dance', 'agility', 'amnesia', 'barrier', 'harden', 'defense_curl']:
                        npc_hp_percent = npc_pokemon['current_hp'] / self._calculate_max_hp(npc_pokemon)
                        if npc_hp_percent > 0.7 and not npc_data.get('status'):
                            # Check if already boosted
                            stat_boosts = npc_data.get('stats', {})
                            stat_map = {
                                'swords_dance': 'attack', 'agility': 'speed', 'amnesia': 'special',
                                'barrier': 'defense', 'harden': 'defense', 'defense_curl': 'defense'
                            }
                            relevant_stat = stat_map.get(move_name, 'attack')
                            if stat_boosts.get(relevant_stat, 0) < 2:
                                score = 45
                            else:
                                score = 5  # Already boosted enough

                    # Status infliction - prioritize if opponent has no status
                    elif move_name in ['sleep_powder', 'thunder_wave', 'toxic', 'poison_powder', 'stun_spore', 'hypnosis', 'sing']:
                        if not player_data.get('status'):
                            score = 50
                            # Extra priority for sleep and paralysis
                            if move_name in ['sleep_powder', 'thunder_wave', 'hypnosis']:
                                score = 60
                        else:
                            score = 5  # Don't waste turn on already statused opponent

                    # Confusion moves
                    elif move_name in ['confuse_ray', 'supersonic']:
                        if not player_data.get('confused'):
                            score = 35
                        else:
                            score = 5  # Don't confuse already confused opponent

                    # Stat reduction moves
                    elif move_name in ['growl', 'leer', 'sand_attack', 'smokescreen']:
                        player_stats = player_data.get('stats', {})
                        stat_map = {
                            'growl': 'attack', 'leer': 'defense',
                            'sand_attack': 'accuracy', 'smokescreen': 'accuracy'
                        }
                        relevant_stat = stat_map.get(move_name, 'attack')
                        if player_stats.get(relevant_stat, 0) > -3:
                            score = 25  # Moderate priority for stat reduction
                        else:
                            score = 5  # Don't over-debuff
                        
            move_scores.append((move_name, score))
            
        # Choose best move with weighted randomness
        # Ensure scores are non-negative before using as weights
        moves = [ms[0] for ms in move_scores]
        weights = [max(0, ms[1]) for ms in move_scores]

        # If all weights are zero, fall back to a simple random choice
        if not any(weights):
            return random.choice(valid_moves)

        # Use weighted random choice
        chosen_move = random.choices(moves, weights=weights, k=1)[0]
        return chosen_move
        
    async def _handle_npc_turn(self, battle_data):
        """Handle NPC turn automatically"""
        await asyncio.sleep(2)  # Dramatic pause
        
        # Check if battle still exists
        npc_id = battle_data['challenger']['id'] if battle_data['challenger']['id'] < 0 else battle_data['opponent']['id']
        if npc_id not in self.active_battles:
            return  # Battle already ended
        
        # Find NPC data
        npc_data = None
        if battle_data['challenger']['id'] < 0:
            npc_data = battle_data['challenger']
        elif battle_data['opponent']['id'] < 0:
            npc_data = battle_data['opponent']
            
        if not npc_data:
            return
            
        # Check if NPC Pokemon is still alive
        npc_pokemon = npc_data['pokemon']
        if npc_pokemon['current_hp'] <= 0:
            # NPC Pokemon is fainted, battle should have ended
            player_id = battle_data['challenger']['id'] if battle_data['challenger']['id'] > 0 else battle_data['opponent']['id']
            await self._end_battle(battle_data, player_id)
            return
            
        # Choose move for NPC using strategic AI
        moves = [npc_pokemon.get('move1'), npc_pokemon.get('move2'), npc_pokemon.get('move3'), npc_pokemon.get('move4')]
        valid_moves = [m for m in moves if m and m in MOVES_DATA]
        
        if valid_moves:
            chosen_move = self._choose_strategic_move(npc_data, battle_data, valid_moves)
            
            try:
                # Execute move
                result_data = await self.use_move(battle_data, npc_data['id'], chosen_move)

                # Send result text
                embed = discord.Embed(description=result_data.get('text', 'An error occurred.'), color=0x3498db)
                await battle_data['channel'].send(embed=embed)

                # Send end embed if it exists
                if result_data.get('end_embed'):
                    await asyncio.sleep(0.1)
                    await battle_data['channel'].send(embed=result_data['end_embed'])

                # Continue battle if not ended and battle still exists
                if npc_id in self.active_battles and battle_data.get('turn'):
                    await asyncio.sleep(1)
                    await self._send_battle_status(battle_data)
            except (discord.HTTPException, aiohttp.ClientOSError) as e:
                logging.warning(f"Failed to send NPC turn message due to network error: {e}")
    
    async def _end_battle(self, battle_data, winner_id):
        # Handle gym battle completion
        gym_cog = self.bot.get_cog('Gym')
        if gym_cog:
            # Check if this is a gym battle
            player_id = battle_data['challenger']['id'] if battle_data['challenger']['id'] > 0 else battle_data['opponent']['id']
            if player_id in gym_cog.active_gym_battles:
                gym_battle_data = gym_cog.active_gym_battles[player_id]
                if winner_id == player_id:
                    return await gym_cog._handle_gym_victory(gym_battle_data)
                else:
                    return await gym_cog._handle_player_loss(gym_battle_data)
        
        # Get IDs from battle data
        challenger_id = battle_data['challenger']['id']
        opponent_id = battle_data['opponent']['id']
        
        # Update battle status in database (only for PvP battles)
        if 'id' in battle_data and challenger_id > 0 and opponent_id > 0:
            try:
                await self.bot.db.execute(
                    "UPDATE battles SET status = 'completed' WHERE id = $1",
                    battle_data['id']
                )
            except Exception as e:
                import logging
                logging.exception(f"Database error updating battle status: {e}")
                pass  # Ignore database errors for battle completion
                
        # Record NPC battle completion for first-time tracking
        elif challenger_id > 0 and opponent_id < 0 and battle_data.get('is_first_completion'):
            npc_type = abs(opponent_id) // 1000
            npc_index = abs(opponent_id) % 1000
            try:
                await self.bot.db.execute(
                    """INSERT INTO npc_completions (user_id, npc_type, npc_index, completed_at) 
                       VALUES ($1, $2, $3, NOW()) ON CONFLICT DO NOTHING""",
                    challenger_id, npc_type, npc_index
                )
            except Exception as e:
                import logging
                logging.info(f"NPC completion tracking failed (table may not exist): {e}")
            
        # Remove from active battles
        if challenger_id in self.active_battles:
            del self.active_battles[challenger_id]
        if opponent_id in self.active_battles:
            del self.active_battles[opponent_id]
            
        # Only award rewards for PvP battles (both IDs positive)
        if challenger_id > 0 and opponent_id > 0:
            # Award experience and money
            winner_pokemon = battle_data['challenger']['pokemon'] if winner_id == challenger_id else battle_data['opponent']['pokemon']
            loser_pokemon = battle_data['opponent']['pokemon'] if winner_id == challenger_id else battle_data['challenger']['pokemon']
            
            exp_gained = (loser_pokemon['level'] * 50) // winner_pokemon['level']
            money_gained = loser_pokemon['level'] * 100
            
            # Award experience (only for real Pokemon)
            if winner_pokemon['id'] > 0:
                new_exp = winner_pokemon['experience'] + exp_gained
                await self.bot.db.execute(
                    "UPDATE pokemon SET experience = $1 WHERE id = $2",
                    new_exp, winner_pokemon['id']
                )
            await self.bot.db.execute(
                "UPDATE users SET money = money + $1 WHERE user_id = $2",
                money_gained, winner_id
            )
            
            embed = discord.Embed(
                title="Battle Ended!",
                description=f"<@{winner_id}> wins the battle!",
                color=0x00ff00
            )
            embed.add_field(name="Experience Gained", value=f"{exp_gained} XP", inline=True)
            embed.add_field(name="Money Gained", value=f"{money_gained} rupees", inline=True)
            
            return embed

        return None

class BattleRequestView(discord.ui.View):
    def __init__(self, bot, challenger_id, opponent_id, challenger_pokemon, opponent_pokemon):
        super().__init__(timeout=60)
        self.bot = bot
        self.challenger_id = challenger_id
        self.opponent_id = opponent_id
        self.challenger_pokemon = challenger_pokemon
        self.opponent_pokemon = opponent_pokemon
        self.message = None
        
    async def on_timeout(self):
        if self.message:
            embed = discord.Embed(
                title="Battle Request Expired",
                description="The battle request has expired.",
                color=0x808080
            )
            self.clear_items()
            try:
                await self.message.edit(embed=embed, view=self)
            except discord.HTTPException:
                pass  # Ignore Discord API errors for message editing
        
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.opponent_id:
            await interaction.response.send_message("This isn't your battle request!", ephemeral=True)
            return
            
        battle_cog = self.bot.get_cog('Battle')
        await battle_cog.start_battle(
            interaction.channel, self.challenger_id, self.opponent_id,
            self.challenger_pokemon, self.opponent_pokemon
        )
        
        self.clear_items()
        await interaction.response.edit_message(content="Battle started!", view=self)
        
    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.opponent_id:
            await interaction.response.send_message("This isn't your battle request!", ephemeral=True)
            return
            
        self.clear_items()
        await interaction.response.edit_message(content="Battle declined.", view=self)

class BattleMoveView(discord.ui.View):
    def __init__(self, bot, battle_data, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.battle_data = battle_data
        self.user_id = user_id
        self.message = None
        
        # Get current Pokemon's moves
        pokemon = self.battle_data['challenger']['pokemon'] if self.user_id == self.battle_data['challenger']['id'] else self.battle_data['opponent']['pokemon']
        moves = [pokemon.get('move1'), pokemon.get('move2'), pokemon.get('move3'), pokemon.get('move4')]
        
        for i, move in enumerate(moves):
            if move:
                button = discord.ui.Button(label=move.replace('_', ' ').title(), custom_id=f"move_{i}")
                button.callback = self._create_move_callback(move)
                self.add_item(button)
                
        # Add switch Pokemon button if user has more than 1 Pokemon
        user_data = self.battle_data['challenger'] if self.user_id == self.battle_data['challenger']['id'] else self.battle_data['opponent']
        available_pokemon = [p for p in user_data['party'] if p['current_hp'] > 0 and p['id'] != user_data['pokemon']['id']]
        
        if available_pokemon:
            switch_button = discord.ui.Button(label="Switch Pokemon", style=discord.ButtonStyle.secondary, custom_id="switch")
            switch_button.callback = self._switch_pokemon
            self.add_item(switch_button)
            
    async def on_timeout(self):
        # Disable all buttons
        for item in self.children:
            item.disabled = True
        
        if self.message:
            try:
                await self.message.edit(view=self)
            except (discord.HTTPException, aiohttp.ClientOSError) as e:
                logging.warning(f"Failed to edit battle message on timeout due to network error: {e}")
            except discord.NotFound:
                pass # Message was deleted, no action needed.
                
    def _create_move_callback(self, move_name):
        async def callback(interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("It's not your turn!", ephemeral=True)
                return

            try:
                battle_cog = self.bot.get_cog('Battle')
                result_data = await battle_cog.use_move(self.battle_data, self.user_id, move_name)

                # Format the result into an embed for better readability
                embed = discord.Embed(description=result_data.get('text', 'An error occurred.'), color=0x3498db)
                await interaction.response.send_message(embed=embed)

                # If there's an end-of-battle embed, send it as a new message.
                if result_data.get('end_embed'):
                    await asyncio.sleep(0.1)  # Ensure message order
                    await self.battle_data['channel'].send(embed=result_data['end_embed'])
                    return  # Battle is over, no need to send new status
                
                # Check if battle still exists (may have ended during move execution)
                if self.user_id not in battle_cog.active_battles:
                    return

                # Small delay to ensure message order
                await asyncio.sleep(0.1)

                # Only continue if battle still exists and has a valid turn
                if self.user_id in battle_cog.active_battles and self.battle_data.get('turn') is not None:
                    await battle_cog._send_battle_status(self.battle_data)
            except (discord.HTTPException, aiohttp.ClientOSError) as e:
                logging.warning(f"Failed to send move result message due to network error: {e}")

        return callback
        
    async def _switch_pokemon(self, interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("It's not your turn!", ephemeral=True)
            return
            
        # Show Pokemon selection
        view = PokemonSwitchView(self.bot, self.battle_data, self.user_id, is_forced=False)
        await interaction.response.send_message("Choose a Pokemon to switch to:", view=view, ephemeral=True)

class PokemonSwitchView(discord.ui.View):
    def __init__(self, bot, battle_data, user_id, is_forced=False):
        super().__init__(timeout=60)
        self.bot = bot
        self.battle_data = battle_data
        self.user_id = user_id
        self.is_forced = is_forced
        
        # Get user's party
        user_data = battle_data['challenger'] if user_id == battle_data['challenger']['id'] else battle_data['opponent']
        
        for i, pokemon in enumerate(user_data['party']):
            if pokemon['current_hp'] > 0 and pokemon['id'] != user_data['pokemon']['id']:
                from data.complete_pokemon_data import COMPLETE_POKEMON_DATA
                species = COMPLETE_POKEMON_DATA[pokemon['species_id']]
                button = discord.ui.Button(
                    label=f"{species['name']} (Lv.{pokemon['level']})",
                    custom_id=f"switch_{i}"
                )
                button.callback = self._create_switch_callback(i)
                self.add_item(button)
                
    def _create_switch_callback(self, pokemon_index):
        async def callback(interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("Not your Pokemon!", ephemeral=True)
                return
                
            # Switch Pokemon
            battle_cog = self.bot.get_cog('Battle')
            user_data = self.battle_data['challenger'] if self.user_id == self.battle_data['challenger']['id'] else self.battle_data['opponent']

            # Reset volatile stats for the side that is switching
            battle_cog._reset_volatile_stats(user_data)

            user_data['pokemon'] = dict(user_data['party'][pokemon_index])
            user_data['current_index'] = pokemon_index
            
            from data.complete_pokemon_data import COMPLETE_POKEMON_DATA
            species = COMPLETE_POKEMON_DATA[user_data['pokemon']['species_id']]
            
            if self.is_forced:
                await interaction.response.send_message(f"Go, {species['name']}!")
                await battle_cog._send_battle_status(self.battle_data)
            else:
                # Voluntary switch - give turn to opponent
                other_user_id = self.battle_data['opponent']['id'] if self.user_id == self.battle_data['challenger']['id'] else self.battle_data['challenger']['id']
                self.battle_data['turn'] = other_user_id
                await interaction.response.send_message(f"Switched to {species['name']}!")
                await battle_cog._send_battle_status(self.battle_data)
                
        return callback

async def setup(bot):
    await bot.add_cog(Battle(bot))