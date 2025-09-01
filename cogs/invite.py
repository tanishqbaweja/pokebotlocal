import discord
from discord.ext import commands
from discord import app_commands

class Invite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="invite", description="Get Professor Byte's invite link")
    async def invite(self, interaction: discord.Interaction):
        invite_link = "https://discord.com/oauth2/authorize?client_id=1405669076260356248&permissions=2147608640&integration_type=0&scope=applications.commands+bot"
        
        embed = discord.Embed(
            title="Invite Professor Byte",
            description=f"Click [here]({invite_link}) to invite Professor Byte to your server!",
            color=0x3498db
        )
        
        try:
            await interaction.user.send(embed=embed)
            await interaction.response.send_message("Invite link sent to your DMs!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(f"I couldn't send you a DM! Here's the invite link: {invite_link}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Invite(bot))