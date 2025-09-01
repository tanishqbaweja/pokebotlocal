import discord
from discord import app_commands
from discord.ext import commands
from data.complete_pokemon_data import COMPLETE_POKEMON_DATA

class Evolution(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Evolution mapping for level-based evolutions
        self.evolution_map = {
            1: 2, 2: 3, 4: 5, 5: 6, 7: 8, 8: 9, 10: 11, 11: 12, 13: 14, 14: 15, 16: 17, 17: 18,
            19: 20, 21: 22, 23: 24, 27: 28, 29: 30, 32: 33, 41: 42, 43: 44, 46: 47, 48: 49,
            50: 51, 52: 53, 54: 55, 56: 57, 60: 61, 63: 64, 66: 67, 69: 70, 72: 73, 74: 75,
            77: 78, 79: 80, 81: 82, 84: 85, 86: 87, 88: 89, 96: 97, 98: 99, 100: 101, 104: 105,
            109: 110, 111: 112, 116: 117, 118: 119, 129: 130, 138: 139, 140: 141, 147: 148, 148: 149
        }
        self.stone_evolutions = {
            'fire_stone': {37: 38, 58: 59, 133: 136},
            'water_stone': {61: 62, 90: 91, 120: 121, 133: 134},
            'thunder_stone': {25: 26, 133: 135},
            'leaf_stone': {44: 45, 70: 71, 102: 103},
            'moon_stone': {30: 31, 33: 34, 35: 36, 39: 40}
        }

    @app_commands.command(name="evolve", description="Evolve a Pokemon using an item")
    async def evolve(self, interaction: discord.Interaction, position: int, item: str):
        user_id = interaction.user.id
        item_name = item.lower().replace(' ', '_')

        if item_name not in self.stone_evolutions:
            await interaction.response.send_message("This item cannot be used for evolution.", ephemeral=True)
            return

        inventory_item = await self.bot.db.fetchrow(
            "SELECT quantity FROM user_inventory WHERE user_id = $1 AND item_name = $2",
            user_id, item_name
        )
        if not inventory_item or inventory_item['quantity'] < 1:
            await interaction.response.send_message(f"You do not have a {item.replace('_', ' ')}.", ephemeral=True)
            return

        pokemon = await self.bot.db.fetchrow(
            "SELECT * FROM pokemon WHERE owner_id = $1 AND in_party = TRUE AND party_position = $2",
            user_id, position
        )
        if not pokemon:
            await interaction.response.send_message(f"No Pokémon at position {position} in your party.", ephemeral=True)
            return

        current_species_id = pokemon['species_id']
        evolved_species_id = self.stone_evolutions[item_name].get(current_species_id)

        if not evolved_species_id:
            await interaction.response.send_message(f"A {item.replace('_', ' ')} will not work on {pokemon['name']}.", ephemeral=True)
            return

        await self.bot.db.execute(
            "UPDATE user_inventory SET quantity = quantity - 1 WHERE user_id = $1 AND item_name = $2",
            user_id, item_name
        )

        await self._evolve_pokemon_with_item(interaction, pokemon, evolved_species_id)

    async def _evolve_pokemon_with_item(self, interaction, pokemon, new_species_id):
        old_species_name = COMPLETE_POKEMON_DATA[pokemon['species_id']]['name']

        await self.bot.db.execute(
            "UPDATE pokemon SET species_id = $1 WHERE id = $2",
            new_species_id, pokemon['id']
        )

        new_species = COMPLETE_POKEMON_DATA[new_species_id]
        old_max_hp = ((COMPLETE_POKEMON_DATA[pokemon['species_id']]['base_hp'] + pokemon['hp_iv']) * 2 * pokemon['level'] // 100) + pokemon['level'] + 10
        new_max_hp = ((new_species['base_hp'] + pokemon['hp_iv']) * 2 * pokemon['level'] // 100) + pokemon['level'] + 10
        hp_increase = new_max_hp - old_max_hp
        new_current_hp = pokemon['current_hp'] + hp_increase

        await self.bot.db.execute(
            "UPDATE pokemon SET current_hp = $1 WHERE id = $2",
            new_current_hp, pokemon['id']
        )

        embed = discord.Embed(
            title="Congratulations!",
            description=f"Your {old_species_name} evolved into {new_species['name']}!",
            color=0xffd700
        )
        await interaction.response.send_message(embed=embed)
        
    @commands.Cog.listener()
    async def on_pokemon_level_up(self, pokemon_id, old_level, new_level, channel_id=None):
        """Handle evolution checks when Pokemon level up"""
        pokemon = await self.bot.db.fetchrow("SELECT * FROM pokemon WHERE id = $1", pokemon_id)
        if not pokemon:
            return

        species_data = COMPLETE_POKEMON_DATA.get(pokemon['species_id'])
        if not species_data or 'evolves_at' not in species_data:
            return
            
        if new_level >= species_data['evolves_at']:
            await self._evolve_pokemon(pokemon, channel_id)
            
    async def _evolve_pokemon(self, pokemon, channel_id=None):
        """Evolve a Pokemon to its next form"""
        new_species_id = self.evolution_map.get(pokemon['species_id'])
        if not new_species_id:
            return
            
        old_species_name = COMPLETE_POKEMON_DATA[pokemon['species_id']]['name']

        await self.bot.db.execute(
            "UPDATE pokemon SET species_id = $1 WHERE id = $2",
            new_species_id, pokemon['id']
        )
        
        new_species = COMPLETE_POKEMON_DATA[new_species_id]
        old_max_hp = ((COMPLETE_POKEMON_DATA[pokemon['species_id']]['base_hp'] + pokemon['hp_iv']) * 2 * pokemon['level'] // 100) + pokemon['level'] + 10
        new_max_hp = ((new_species['base_hp'] + pokemon['hp_iv']) * 2 * pokemon['level'] // 100) + pokemon['level'] + 10
        hp_increase = new_max_hp - old_max_hp
        new_current_hp = pokemon['current_hp'] + hp_increase
        
        await self.bot.db.execute(
            "UPDATE pokemon SET current_hp = $1 WHERE id = $2",
            new_current_hp, pokemon['id']
        )
        
        embed = discord.Embed(
            title="Evolution!",
            description=f"Your {old_species_name} evolved into {new_species['name']}!",
            color=0xffd700
        )

        channel = self.bot.get_channel(channel_id) if channel_id else None
        if channel:
            await channel.send(embed=embed)
        else:
            # Fallback to DM
            try:
                user = await self.bot.fetch_user(pokemon['owner_id'])
                if user:
                    await user.send(embed=embed)
            except Exception as e:
                import logging
                logging.info(f"Could not send evolution DM to user {pokemon['owner_id']}: {e}")

async def setup(bot):
    await bot.add_cog(Evolution(bot))