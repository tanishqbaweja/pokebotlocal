import discord
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
        # Item-based evolutions
        self.item_evolution_map = {
            'fire_stone': {37: 38, 58: 59, 133: 136}, # Vulpix, Growlithe, Eevee
            'water_stone': {61: 62, 90: 91, 120: 121, 133: 134}, # Poliwhirl, Shellder, Staryu, Eevee
            'thunder_stone': {25: 26, 133: 135}, # Pikachu, Eevee
            'leaf_stone': {44: 45, 70: 71, 102: 103}, # Gloom, Weepinbell, Exeggcute
            'moon_stone': {30: 31, 33: 34, 35: 36, 39: 40} # Nidorina, Nidorino, Clefairy, Jigglypuff
        }
        
    @commands.Cog.listener()
    async def on_pokemon_level_up(self, pokemon, old_level, new_level, channel_id=None):
        """Handle evolution checks when a Pokemon levels up."""
        species_data = COMPLETE_POKEMON_DATA.get(pokemon['species_id'])
        if not species_data or 'evolves_at' not in species_data:
            return
            
        if new_level >= species_data['evolves_at']:
            channel = self.bot.get_channel(channel_id) if channel_id else None
            await self._evolve_pokemon(pokemon, channel)
            
    async def _evolve_pokemon(self, pokemon, channel=None, item_name=None):
        """Evolve a Pokemon to its next form and notify the user."""
        current_species_id = pokemon['species_id']
        new_species_id = None

        if item_name:
            # Item-based evolution
            if item_name in self.item_evolution_map and current_species_id in self.item_evolution_map[item_name]:
                new_species_id = self.item_evolution_map[item_name][current_species_id]
        else:
            # Level-up evolution
            new_species_id = self.evolution_map.get(current_species_id)

        if not new_species_id:
            return
            
        # Update Pokemon species
        await self.bot.db.execute(
            "UPDATE pokemon SET species_id = $1 WHERE id = $2",
            new_species_id, pokemon['id']
        )
        
        # Correctly recalculate HP
        old_species_data = COMPLETE_POKEMON_DATA[current_species_id]
        new_species_data = COMPLETE_POKEMON_DATA[new_species_id]

        old_max_hp = ((old_species_data['base_hp'] + pokemon['hp_iv']) * 2 * pokemon['level'] // 100) + pokemon['level'] + 10
        new_max_hp = ((new_species_data['base_hp'] + pokemon['hp_iv']) * 2 * pokemon['level'] // 100) + pokemon['level'] + 10

        hp_increase = new_max_hp - old_max_hp
        new_current_hp = pokemon['current_hp'] + hp_increase
        
        await self.bot.db.execute(
            "UPDATE pokemon SET current_hp = $1 WHERE id = $2",
            new_current_hp, pokemon['id']
        )
        
        # Notify in channel
        if channel:
            old_name = old_species_data['name']
            new_name = new_species_data['name']
            embed = discord.Embed(
                title="Evolution!",
                description=f"<@{pokemon['owner_id']}>'s {old_name} evolved into {new_name}!",
                color=0xffd700
            )
            await channel.send(embed=embed)

    @app_commands.command(name="evolve", description="Use an evolution stone on a compatible Pokémon.")
    @app_commands.describe(position="The party position of the Pokémon to evolve.", item="The evolution stone to use.")
    async def evolve(self, interaction: discord.Interaction, position: int, item: str):
        user_id = interaction.user.id
        # Standardize item name, but handle cases where user might already add "_stone"
        item_name = item.lower().replace(" ", "_")
        if not item_name.endswith("_stone"):
            item_name += "_stone"

        if item_name not in self.item_evolution_map:
            await interaction.response.send_message("This is not a valid evolution stone.", ephemeral=True)
            return

        # Check if user has the item
        item_record = await self.bot.db.fetchrow("SELECT quantity FROM user_inventory WHERE user_id = $1 AND item_name = $2", user_id, item_name)
        if not item_record or item_record['quantity'] < 1:
            await interaction.response.send_message(f"You do not have a {item.replace('_', ' ').title()}.", ephemeral=True)
            return

        # Get the pokemon
        if not (1 <= position <= 6):
            await interaction.response.send_message("Invalid party position.", ephemeral=True)
            return
        pokemon = await self.bot.db.fetchrow("SELECT * FROM pokemon WHERE owner_id = $1 AND in_party = TRUE AND party_position = $2", user_id, position)
        if not pokemon:
            await interaction.response.send_message(f"You don't have a Pokémon at party position {position}.", ephemeral=True)
            return

        # Check for compatibility
        compatible_evolutions = self.item_evolution_map[item_name]
        if pokemon['species_id'] not in compatible_evolutions:
            await interaction.response.send_message(f"A {item.replace('_', ' ').title()} cannot be used on this Pokémon.", ephemeral=True)
            return

        # Consume the item and evolve the pokemon
        try:
            await self.bot.db.execute("BEGIN")

            # Decrement item quantity
            await self.bot.db.execute(
                "UPDATE user_inventory SET quantity = quantity - 1 WHERE user_id = $1 AND item_name = $2",
                user_id, item_name
            )

            await self._evolve_pokemon(pokemon, interaction.channel, item_name=item_name)

            await self.bot.db.execute("COMMIT")

        except Exception as e:
            await self.bot.db.execute("ROLLBACK")
            await interaction.response.send_message(f"An error occurred during evolution: {e}", ephemeral=True)
            return

        # The notification is handled in _evolve_pokemon now
        await interaction.response.send_message("Evolution process completed.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Evolution(bot))