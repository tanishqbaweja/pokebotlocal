import discord
from discord.ext import commands
from discord import app_commands

class HelpSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="help", description="Show a complete list of bot commands")
    async def help_command(self, interaction: discord.Interaction):
        
        embed = discord.Embed(
            title="Professor Byte Command Guide",
            description="Here is a full list of available commands.",
            color=0x42bcf5
        )

        # Core Commands
        embed.add_field(
            name="🏁 Getting Started",
            value="`/start` - Begin your Pokémon journey!\n"
                  "`/profile` - View your trainer profile.\n"
                  "`/party` - View your current party of Pokémon.",
            inline=False
        )

        # Pokémon Management
        embed.add_field(
            name="🐾 Pokémon & Storage",
            value="`/catch [pokeball]` - Catch a wild Pokémon.\n"
                  "`/pokebox [page]` - View your Pokémon storage.\n"
                  "`/deposit [position]` - Move a Pokémon from your party to the PC.\n"
                  "`/withdraw [pokemon_id]` - Move a Pokémon from the PC to your party.\n"
                  "`/switch [pos1] [pos2]` - Switch the positions of two Pokémon in your party.\n"
                  "`/stats [position]` - View a Pokémon's stats and moves.",
            inline=False
        )

        # Evolution & Moves
        embed.add_field(
            name="✨ Evolution & Moves",
            value="`/evolve [position] [item]` - Use an evolution stone on a Pokémon.\n"
                  "`/teach [position] [move_item]` - Teach a TM or HM move to a Pokémon.\n"
                  "`/choosemove` - Choose which move to replace when learning a new one.\n"
                  "`/forgetmove` - Skip learning a new move.",
            inline=False
        )

        # Battle & Trading
        embed.add_field(
            name="⚔️ Battle & Trading",
            value="`/battle [opponent]` - Challenge another trainer to a battle.\n"
                  "`/trade [user] [position]` - Offer to trade a Pokémon with another user.",
            inline=False
        )

        # Gym Progression
        embed.add_field(
            name="🏆 Gyms & The Pokémon League",
            value="`/gym [leader]` - Challenge one of the 8 Kanto Gym Leaders.\n"
                  "`/elite4 [member]` - Challenge a member of the Elite Four.\n"
                  "`/champion` - Challenge the Pokémon League Champion.",
            inline=False
        )

        # Economy
        embed.add_field(
            name="💰 Shop & Items",
            value="`/shop [page]` - View items available for purchase.\n"
                  "`/buy [item] [quantity]` - Purchase items from the shop.\n"
                  "`/sell [item] [quantity]` - Sell items to the shop.\n"
                  "`/inventory [page]` - View your items.\n"
                  "`/use [item] [position]` - Use a consumable item on a Pokémon.\n"
                  "`/healall` - Use potions from your inventory to heal your entire party.",
            inline=False
        )

        # Utility
        embed.add_field(
            name="🔧 Utilities",
            value="`/pokedex [page]` - View your Pokédex completion progress.\n"
                  "`/defaultpokeball [type]` - Set your default pokéball for `/catch`.\n"
                  "`/invite` - Get the bot's invite link.\n"
                  "`/server` - Get the invite link for the official support server.",
            inline=False
        )

        # Admin Commands (conditionally shown)
        if interaction.user.guild_permissions.administrator:
            embed.add_field(
                name="🔒 Admin Commands",
                value="`/setspawn ...` - Configure channels for Pokémon spawns.\n"
                      "`/spawn ...` - Force a Pokémon to spawn.\n"
                      "`/givemoney ...` - Give money to a user.\n"
                      "`/giveitem ...` - Give an item to a user.\n"
                      "`/resetuser ...` - Reset a user's progress.\n"
                      "`/setlevel ...` - Set a Pokémon's level.",
                inline=False
            )
            
        embed.set_footer(text="Good luck, trainer!")

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(HelpSystem(bot))