import discord
from discord.ext import commands
import traceback
import logging

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_application_command_error(self, interaction: discord.Interaction, error):
        """Handle slash command errors"""
        if isinstance(error, commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"Command is on cooldown. Try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
        elif isinstance(error, commands.MissingPermissions):
            await interaction.response.send_message(
                "You don't have permission to use this command!",
                ephemeral=True
            )
        elif isinstance(error, commands.BotMissingPermissions):
            await interaction.response.send_message(
                "I don't have the required permissions to execute this command!",
                ephemeral=True
            )
        elif isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        else:
            # Log unexpected errors
            logging.error(f"Unexpected error in {interaction.command}: {error}")
            logging.error(traceback.format_exc())
            
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "An unexpected error occurred. Please try again later.",
                    ephemeral=True
                )
                
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Handle prefix command errors"""
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command!")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I don't have the required permissions to execute this command!")
        elif isinstance(error, commands.CommandNotFound):
            return  # Ignore unknown commands
        else:
            # Log unexpected errors
            logging.error(f"Unexpected error in {ctx.command}: {error}")
            logging.error(traceback.format_exc())
            await ctx.send("An unexpected error occurred. Please try again later.")

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))