import discord
from discord.ext import commands
from discord import app_commands

class Statistics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="trainerstats", description="View detailed trainer statistics")
    async def trainerstats(self, interaction: discord.Interaction, user: discord.Member = None):
        target_user = user or interaction.user
        user_id = target_user.id
        
        # Get user data
        user_data = await self.bot.db.get_user(user_id)
        if not user_data:
            await interaction.response.send_message(f"{target_user.display_name} hasn't started their journey yet!", ephemeral=True)
            return
            
        # Get Pokemon statistics in single query for better performance
        stats = await self.bot.db.fetchrow(
            """SELECT 
                COUNT(*) as total_pokemon,
                COUNT(CASE WHEN in_party = TRUE THEN 1 END) as party_pokemon,
                COUNT(CASE WHEN is_shiny = TRUE THEN 1 END) as shiny_pokemon,
                COUNT(DISTINCT species_id) as caught_species
               FROM pokemon WHERE owner_id = $1""",
            user_id
        )
        
        total_pokemon = stats['total_pokemon'] if stats else 0
        party_pokemon = stats['party_pokemon'] if stats else 0
        shiny_pokemon = stats['shiny_pokemon'] if stats else 0
        caught_species = stats['caught_species'] if stats else 0
        
        # Get highest level Pokemon
        highest_level = await self.bot.db.fetchrow(
            """SELECT p.level, ps.name FROM pokemon p 
               JOIN pokemon_species ps ON p.species_id = ps.id
               WHERE p.owner_id = $1 ORDER BY p.level DESC LIMIT 1""",
            user_id
        )
        
        embed = discord.Embed(
            title=f"{target_user.display_name}'s Statistics",
            color=0x3498db
        )
        
        # Basic stats
        embed.add_field(name="💰 Money", value=f"{user_data['money']:,} rupees", inline=True)
        embed.add_field(name="🏆 Badges", value=f"{user_data['badges']}", inline=True)
        embed.add_field(name="🎒 Party", value=f"{party_pokemon}/6", inline=True)
        
        # Pokemon stats
        embed.add_field(name="📦 Total Pokemon", value=f"{total_pokemon}", inline=True)
        embed.add_field(name="✨ Shiny Pokemon", value=f"{shiny_pokemon}", inline=True)
        embed.add_field(name="📚 Species Caught", value=f"{caught_species}/151", inline=True)
        
        if highest_level:
            embed.add_field(
                name="⭐ Highest Level",
                value=f"Level {highest_level['level']} {highest_level['name']}",
                inline=False
            )
            
        # Progress bar for Pokedex
        progress = (caught_species / 151) * 100
        progress_bar = "█" * int(progress // 5) + "░" * (20 - int(progress // 5))
        embed.add_field(
            name="📖 Pokedex Progress",
            value=f"`{progress_bar}` {progress:.1f}%",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="leaderboard", description="View server leaderboards")
    async def leaderboard(self, interaction: discord.Interaction, category: str = "money"):
        category = category.lower()
        
        if category == "money":
            users = await self.bot.db.fetch(
                "SELECT user_id, username, money FROM users ORDER BY money DESC LIMIT 10"
            )
            title = "💰 Money Leaderboard"
            value_format = lambda x: f"{x['money']:,} rupees"
            
        elif category == "badges":
            users = await self.bot.db.fetch(
                "SELECT user_id, username, badges FROM users ORDER BY badges DESC LIMIT 10"
            )
            title = "🏆 Badge Leaderboard"
            value_format = lambda x: f"{x['badges']} badges"
            
        elif category == "pokemon":
            users = await self.bot.db.fetch(
                """SELECT u.user_id, u.username, COUNT(p.id) as pokemon_count
                   FROM users u LEFT JOIN pokemon p ON u.user_id = p.owner_id
                   GROUP BY u.user_id, u.username
                   ORDER BY pokemon_count DESC LIMIT 10"""
            )
            title = "📦 Pokemon Collection Leaderboard"
            value_format = lambda x: f"{x['pokemon_count']} Pokemon"
            
        else:
            await interaction.response.send_message("Invalid category! Use: money, badges, or pokemon", ephemeral=True)
            return
            
        embed = discord.Embed(title=title, color=0xffd700)
        
        if not users:
            embed.description = "No data available yet!"
        else:
            leaderboard_text = ""
            for i, user in enumerate(users, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                leaderboard_text += f"{medal} **{user['username']}** - {value_format(user)}\n"
                
            embed.description = leaderboard_text
            
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Statistics(bot))