import discord
from discord.ext import commands
import random
from data.complete_pokemon_data import COMPLETE_POKEMON_DATA as POKEMON_DATA

class StatusEffects(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    def apply_status_damage(self, pokemon_data, battle_data):
        """Apply status effect damage/effects"""
        pokemon = pokemon_data['pokemon']
        status = pokemon_data.get('status')
        result_messages = []
        
        if status == 'burn':
            damage = max(1, pokemon['current_hp'] // 16)
            pokemon['current_hp'] = max(0, pokemon['current_hp'] - damage)
            result_messages.append(f"{pokemon['name']} is hurt by burn! ({damage} damage)")
            
        elif status == 'poison':
            damage = max(1, pokemon['current_hp'] // 8)
            pokemon['current_hp'] = max(0, pokemon['current_hp'] - damage)
            result_messages.append(f"{pokemon['name']} is hurt by poison! ({damage} damage)")
            
        elif status == 'sleep':
            pokemon_data['status_turns'] -= 1
            if pokemon_data['status_turns'] <= 0:
                pokemon_data['status'] = None
                result_messages.append(f"{pokemon['name']} woke up!")
            else:
                result_messages.append(f"{pokemon['name']} is fast asleep!")
                
        # Handle confusion
        if pokemon_data.get('confused'):
            pokemon_data['confusion_turns'] -= 1
            if pokemon_data['confusion_turns'] <= 0:
                pokemon_data['confused'] = False
                result_messages.append(f"{pokemon['name']} snapped out of confusion!")
            elif random.randint(1, 2) == 1:  # 50% chance to hurt itself
                damage = pokemon['current_hp'] // 8
                pokemon['current_hp'] = max(0, pokemon['current_hp'] - damage)
                result_messages.append(f"{pokemon['name']} hurt itself in confusion! ({damage} damage)")
                
        # Handle Leech Seed
        if pokemon_data.get('seeded'):
            damage = max(1, pokemon['current_hp'] // 8)
            pokemon['current_hp'] = max(0, pokemon['current_hp'] - damage)
            # Find opponent to heal
            opponent_data = battle_data['opponent'] if pokemon_data == battle_data['challenger'] else battle_data['challenger']
            opponent_pokemon = opponent_data['pokemon']
            max_hp = ((POKEMON_DATA[opponent_pokemon['species_id']]['base_hp'] + opponent_pokemon['hp_iv']) * 2 * opponent_pokemon['level'] // 100) + opponent_pokemon['level'] + 10
            heal_amount = min(damage, max_hp - opponent_pokemon['current_hp'])
            opponent_pokemon['current_hp'] += heal_amount
            result_messages.append(f"{pokemon['name']} is hurt by Leech Seed! {opponent_pokemon['name']} recovered {heal_amount} HP!")
            
        return "\n".join(result_messages) if result_messages else None
        
    def can_use_move(self, pokemon_data):
        """Check if Pokemon can use a move based on status"""
        status = pokemon_data.get('status')
        
        if status == 'freeze':
            if random.randint(1, 5) == 1:  # 20% chance to thaw
                pokemon_data['status'] = None
                return True, f"{pokemon_data['pokemon']['name']} thawed out!"
            return False, f"{pokemon_data['pokemon']['name']} is frozen solid!"
            
        elif status == 'paralysis':
            if random.randint(1, 4) == 1:  # 25% chance to be fully paralyzed
                return False, f"{pokemon_data['pokemon']['name']} is paralyzed and can't move!"
            return True, None
            
        elif status == 'sleep':
            return False, f"{pokemon_data['pokemon']['name']} is fast asleep!"
            
        # Check confusion
        if pokemon_data.get('confused') and random.randint(1, 2) == 1:
            return False, f"{pokemon_data['pokemon']['name']} is confused!"
            
        return True, None
        
    def modify_damage(self, damage, attacker_status):
        """Modify damage based on attacker's status"""
        if attacker_status == 'burn':
            return damage // 2  # Burn halves physical attack damage
        return damage

async def setup(bot):
    await bot.add_cog(StatusEffects(bot))