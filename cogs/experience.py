import discord
from discord.ext import commands
import random
from data.complete_pokemon_data import COMPLETE_POKEMON_DATA as POKEMON_DATA, EXP_GROUPS

class Experience(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
            
        user_id = message.author.id
        user = await self.bot.db.get_user(user_id)
        
        if not user:
            return
            
        # Award XP and money (significantly increased XP gain)
        xp_gained = random.randint(200, 400)
        money_gained = random.randint(5, 10)
        
        # Get fresh party Pokemon (in case party changed)
        party = await self.bot.db.get_user_pokemon(user_id, in_party=True)
        
        if party:
            # Filter out level 100 Pokemon
            eligible_pokemon = [p for p in party if p['level'] < 100]
            
            if eligible_pokemon:
                xp_per_pokemon = xp_gained // len(eligible_pokemon)
                
                for pokemon in eligible_pokemon:
                    await self._add_experience(pokemon, xp_per_pokemon, message.channel)
                

                
        # Award money
        await self.bot.db.execute(
            "UPDATE users SET money = money + $1 WHERE user_id = $2",
            money_gained, user_id
        )
        
    async def _add_experience(self, pokemon, exp_amount, message_channel=None):
        if pokemon['level'] >= 100:
            return  # Don't add XP to level 100 Pokemon
            
        new_exp = pokemon['experience'] + exp_amount
        current_level = pokemon['level']
        
        # Check for level up
        species = POKEMON_DATA[pokemon['species_id']]
        exp_formula = EXP_GROUPS[species['exp_group']]
        
        new_level = current_level
        while new_level < 100:
            exp_needed = exp_formula(new_level + 1)
            if new_exp >= exp_needed:
                new_level += 1
            else:
                break
                
        # Update Pokemon in database
        await self.bot.db.execute(
            "UPDATE pokemon SET experience = $1, level = $2 WHERE id = $3",
            new_exp, new_level, pokemon['id']
        )
        

        
        # Create mutable copy for further processing
        pokemon_dict = dict(pokemon)
        pokemon_dict['experience'] = new_exp
        pokemon_dict['level'] = new_level
        pokemon_dict['current_hp'] = pokemon['current_hp']  # Ensure current_hp is included
        
        # Level up notification and evolution check
        if new_level > current_level:
            await self._handle_level_up(pokemon_dict, current_level, new_level)
            
            # Send level-up notification to server channel
            species_name = POKEMON_DATA[pokemon_dict['species_id']]['name']
            
            if message_channel:
                await message_channel.send(f"🎉 **{species_name}** leveled up to level **{new_level}**!")
            
            # Check for evolution using proper evolution mapping
            species = POKEMON_DATA[pokemon_dict['species_id']]
            if 'evolves_at' in species and new_level >= species['evolves_at']:
                evolution_cog = self.bot.get_cog('Evolution')
                if evolution_cog and hasattr(evolution_cog, 'evolution_map'):
                    evolved_species_id = evolution_cog.evolution_map.get(pokemon_dict['species_id'])
                    if evolved_species_id and evolved_species_id in POKEMON_DATA:
                        await evolution_cog._evolve_pokemon(pokemon_dict)
                        if message_channel:
                            evo_species = POKEMON_DATA[evolved_species_id]
                            await message_channel.send(f"🎆 **{species_name}** evolved into **{evo_species['name']}**!")
            
            # Trigger evolution and move learning events
            self.bot.dispatch('pokemon_level_up', pokemon_dict['id'], current_level, new_level)
            
    async def _handle_level_up(self, pokemon, old_level, new_level):
        # Recalculate HP
        species = POKEMON_DATA[pokemon['species_id']]
        new_max_hp = ((species['base_hp'] + pokemon['hp_iv']) * 2 * new_level // 100) + new_level + 10
        hp_increase = new_max_hp - self._calculate_max_hp_at_level(pokemon, old_level)
        
        new_current_hp = pokemon['current_hp'] + hp_increase
        
        await self.bot.db.execute(
            "UPDATE pokemon SET current_hp = $1 WHERE id = $2",
            new_current_hp, pokemon['id']
        )
        
        # Move learning is now handled by the MoveLearning cog
        
    def _calculate_max_hp_at_level(self, pokemon, level):
        species = POKEMON_DATA[pokemon['species_id']]
        return ((species['base_hp'] + pokemon['hp_iv']) * 2 * level // 100) + level + 10

async def setup(bot):
    await bot.add_cog(Experience(bot))