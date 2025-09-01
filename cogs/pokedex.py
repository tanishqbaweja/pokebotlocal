import discord
from discord.ext import commands
from discord import app_commands
import math
from data.complete_pokemon_data import COMPLETE_POKEMON_DATA as POKEMON_DATA

class Pokedex(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="pokedex", description="View your Pokedex progress")
    async def pokedex(self, interaction: discord.Interaction, page: int = 1):
        user_id = interaction.user.id
        
        # Get caught and seen Pokemon
        caught_pokemon = await self.bot.db.fetch(
            "SELECT DISTINCT species_id FROM pokemon WHERE owner_id = $1",
            user_id
        )
        caught_ids = {row['species_id'] for row in caught_pokemon}
        
        # For now, seen = caught (can be expanded later)
        seen_ids = caught_ids
        
        # Pagination
        per_page = 20
        total_pokemon = len(POKEMON_DATA)
        total_pages = math.ceil(total_pokemon / per_page)
        page = max(1, min(page, total_pages))
        
        start_idx = (page - 1) * per_page + 1
        end_idx = min(start_idx + per_page - 1, total_pokemon)
        
        embed = discord.Embed(
            title=f"Pokedex - Page {page}/{total_pages}",
            description=f"Caught: {len(caught_ids)}/{total_pokemon} | Seen: {len(seen_ids)}/{total_pokemon}",
            color=0x3498db
        )
        
        pokedex_text = ""
        for pokemon_id in range(start_idx, end_idx + 1):
            if pokemon_id in POKEMON_DATA:
                pokemon = POKEMON_DATA[pokemon_id]
                if pokemon_id in caught_ids:
                    status = "🔴"  # Caught
                elif pokemon_id in seen_ids:
                    status = "🟡"  # Seen
                else:
                    status = "⚫"  # Unknown
                    
                name = pokemon['name'] if pokemon_id in seen_ids else "???"
                pokedex_text += f"{status} #{pokemon_id:03d} {name}\n"
                
        embed.add_field(name="Pokemon", value=pokedex_text, inline=False)
        embed.set_footer(text="🔴 Caught | 🟡 Seen | ⚫ Unknown")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Pokedex(bot))