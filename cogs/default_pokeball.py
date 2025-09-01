import discord
from discord.ext import commands
from discord import app_commands

class DefaultPokeball(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="defaultpokeball", description="Set your default pokeball type")
    async def default_pokeball(self, interaction: discord.Interaction, pokeball_type: str = None):
        user_id = interaction.user.id
        
        if not pokeball_type:
            # Show current default
            user = await self.bot.db.get_user(user_id)
            if user:
                await interaction.response.send_message(f"Your default pokeball is: **{user['default_pokeball']}**", ephemeral=True)
            else:
                await interaction.response.send_message("You haven't started your journey yet! Use `/start` to begin.", ephemeral=True)
            return
            
        # Check if user exists
        user = await self.bot.db.get_user(user_id)
        if not user:
            await interaction.response.send_message("You haven't started your journey yet! Use `/start` to begin.", ephemeral=True)
            return
            
        # Validate pokeball type
        valid_pokeballs = ["pokeball", "greatball", "ultraball", "masterball"]
        pokeball_type = pokeball_type.lower()
        if pokeball_type not in valid_pokeballs:
            await interaction.response.send_message(f"Invalid pokeball type! Valid types: {', '.join(valid_pokeballs)}", ephemeral=True)
            return
            
        # Update default pokeball
        await self.bot.db.execute(
            "UPDATE users SET default_pokeball = $1 WHERE user_id = $2",
            pokeball_type.lower(), user_id
        )
        
        await interaction.response.send_message(f"Default pokeball set to: **{pokeball_type.lower()}**")

async def setup(bot):
    await bot.add_cog(DefaultPokeball(bot))