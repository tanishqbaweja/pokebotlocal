import discord
from discord.ext import commands
from data.complete_pokemon_data import COMPLETE_POKEMON_DATA

class Evolution(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Evolution mapping for level-based evolutions
        self.evolution_map = {
            # Starter evolutions
            1: 2, 2: 3,    # Bulbasaur line
            4: 5, 5: 6,    # Charmander line  
            7: 8, 8: 9,    # Squirtle line
            
            # Common evolutions
            10: 11, 11: 12,  # Caterpie line
            13: 14, 14: 15,  # Weedle line
            16: 17, 17: 18,  # Pidgey line
            19: 20,          # Rattata -> Raticate
            21: 22,          # Spearow -> Fearow
            23: 24,          # Ekans -> Arbok
            27: 28,          # Sandshrew -> Sandslash
            29: 30,          # Nidoran♀ -> Nidorina
            32: 33,          # Nidoran♂ -> Nidorino
            41: 42,          # Zubat -> Golbat
            43: 44,          # Oddish -> Gloom
            46: 47,          # Paras -> Parasect
            48: 49,          # Venonat -> Venomoth
            50: 51,          # Diglett -> Dugtrio
            52: 53,          # Meowth -> Persian
            54: 55,          # Psyduck -> Golduck
            56: 57,          # Mankey -> Primeape
            60: 61,          # Poliwag -> Poliwhirl
            63: 64,          # Abra -> Kadabra
            66: 67,          # Machop -> Machoke
            69: 70,          # Bellsprout -> Weepinbell
            72: 73,          # Tentacool -> Tentacruel
            74: 75,          # Geodude -> Graveler
            77: 78,          # Ponyta -> Rapidash
            79: 80,          # Slowpoke -> Slowbro
            81: 82,          # Magnemite -> Magneton
            84: 85,          # Doduo -> Dodrio
            86: 87,          # Seel -> Dewgong
            88: 89,          # Grimer -> Muk
            96: 97,          # Drowzee -> Hypno
            98: 99,          # Krabby -> Kingler
            100: 101,        # Voltorb -> Electrode
            104: 105,        # Cubone -> Marowak
            109: 110,        # Koffing -> Weezing
            111: 112,        # Rhyhorn -> Rhydon
            116: 117,        # Horsea -> Seadra
            118: 119,        # Goldeen -> Seaking
            129: 130,        # Magikarp -> Gyarados
            138: 139,        # Omanyte -> Omastar
            140: 141,        # Kabuto -> Kabutops
            147: 148, 148: 149  # Dratini line
        }
        
    @commands.Cog.listener()
    async def on_pokemon_level_up(self, pokemon_id, old_level, new_level):
        """Handle evolution checks when Pokemon level up"""
        pokemon = await self.bot.db.fetchrow("SELECT * FROM pokemon WHERE id = $1", pokemon_id)
        if not pokemon:
            return
            
        species_data = COMPLETE_POKEMON_DATA.get(pokemon['species_id'])
        if not species_data or 'evolves_at' not in species_data:
            return
            
        if new_level >= species_data['evolves_at']:
            await self._evolve_pokemon(pokemon)
            
    async def _evolve_pokemon(self, pokemon):
        """Evolve a Pokemon to its next form"""
        new_species_id = self.evolution_map.get(pokemon['species_id'])
        if not new_species_id:
            return
            
        # Update Pokemon species
        await self.bot.db.execute(
            "UPDATE pokemon SET species_id = $1 WHERE id = $2",
            new_species_id, pokemon['id']
        )
        
        # Recalculate HP for new species
        new_species = COMPLETE_POKEMON_DATA[new_species_id]
        new_max_hp = ((new_species['base_hp'] + pokemon['hp_iv']) * 2 * pokemon['level'] // 100) + pokemon['level'] + 10
        hp_increase = new_max_hp - pokemon['current_hp']
        
        await self.bot.db.execute(
            "UPDATE pokemon SET current_hp = current_hp + $1 WHERE id = $2",
            max(0, hp_increase), pokemon['id']
        )
        
        # Notify owner
        owner = await self.bot.db.fetchrow("SELECT * FROM users WHERE user_id = $1", pokemon['owner_id'])
        if owner:
            try:
                user = self.bot.get_user(pokemon['owner_id'])
                if user:
                    old_species = COMPLETE_POKEMON_DATA[pokemon['species_id']]
                    embed = discord.Embed(
                        title="Evolution!",
                        description=f"Your {old_species['name']} evolved into {new_species['name']}!",
                        color=0xffd700
                    )
                    await user.send(embed=embed)
            except Exception as e:
                import logging
                logging.info(f"Could not send evolution DM to user {pokemon['owner_id']}: {e}")

async def setup(bot):
    await bot.add_cog(Evolution(bot))