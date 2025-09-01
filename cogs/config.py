import discord
from discord.ext import commands
from discord import app_commands

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="defaultpokeball", description="Set your default Pokeball type")
    async def default_pokeball(self, ctx, ball_type: str):
        user_id = ctx.author.id
        ball_type = ball_type.lower()

        valid_balls = ['pokeball', 'greatball', 'ultraball', 'masterball']
        if ball_type not in valid_balls:
            await ctx.send(f"Invalid ball type! Valid options: {', '.join(valid_balls)}", ephemeral=True)
            return

        # Check if user exists
        user = await self.bot.db.get_user(user_id)
        if not user:
            await ctx.send("You haven't started your journey yet! Use `/start` to begin.", ephemeral=True)
            return

        # Update default pokeball
        try:
            await self.bot.db.execute(
                "UPDATE users SET default_pokeball = $1 WHERE user_id = $2",
                ball_type, user_id
            )
        except Exception as e:
            import logging
            logging.exception(f"Database error updating default pokeball: {e}")
            await ctx.send("Failed to update default pokeball. Please try again.", ephemeral=True)
            return

        await ctx.send(f"Set default Pokeball to {ball_type.title()}!")

async def setup(bot):
    await bot.add_cog(Config(bot))