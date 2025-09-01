import discord
from discord.ext import commands
from discord import app_commands

class HelpSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admin_id = 408190648924110858
        
    def is_admin(self, user_id):
        return user_id == self.admin_id
        
    @app_commands.command(name="help", description="Show bot commands and information")
    @app_commands.describe(category="Choose a help category")
    @app_commands.choices(category=[
        app_commands.Choice(name="Basic Commands", value="basic"),
        app_commands.Choice(name="Pokemon Management", value="pokemon"),
        app_commands.Choice(name="Battle System", value="battle"),
        app_commands.Choice(name="Economy & Items", value="economy"),
        app_commands.Choice(name="Gym Challenges", value="gym"),
        app_commands.Choice(name="Trading System", value="trading"),
        app_commands.Choice(name="Admin Commands", value="admin")
    ])
    async def help_command(self, interaction: discord.Interaction, category: str = None):
        if not category:
            embed = discord.Embed(
                title="🎮 Professor Byte Help",
                description="Welcome to Professor Byte! Choose a category below to view commands.",
                color=0xff6b6b
            )
            
            embed.add_field(
                name="📚 **Command Categories**",
                value="🎯 `/help basic` - Getting started & profiles\n"
                      "🎒 `/help pokemon` - Pokemon management & storage\n"
                      "⚔️ `/help battle` - PvP battles & combat\n"
                      "🛒 `/help economy` - Shop, items & inventory\n"
                      "🏆 `/help gym` - Gym leaders & Elite Four\n"
                      "🔄 `/help trading` - Pokemon trading system\n"
                      "⚙️ `/help admin` - Admin commands",
                inline=False
            )
            
            embed.add_field(
                name="⚙️ **Server Setup (Admins)**",
                value="🔧 **Server admins must use `/setspawn #channel` first to enable Professor Byte functionality!**\n"
                      "This sets where Pokemon will spawn and activates Professor Byte.",
                inline=False
            )
            
            embed.add_field(
                name="🚀 **Quick Start Guide**",
                value="1️⃣ Use `/start` to begin your Pokemon journey\n"
                      "2️⃣ Choose your starter Pokemon (Bulbasaur, Charmander, or Squirtle)\n"
                      "3️⃣ Catch wild Pokemon with `/catch` in spawn channels\n"
                      "4️⃣ Battle other trainers with `/battle @user`\n"
                      "5️⃣ Challenge gym leaders with `/gym [leader]`\n"
                      "6️⃣ Build your collection and become Champion!",
                inline=False
            )
            
            embed.set_footer(text="💡 Tip: Use /help [category] for detailed command lists!")
            
        elif category.lower() == "basic":
            embed = discord.Embed(
                title="🎯 Basic Commands", 
                description="Essential commands to get started on your Pokemon journey!",
                color=0x4ecdc4
            )
            embed.add_field(
                name="🚀 **Getting Started**",
                value="🎮 `/start` - Begin your Pokemon journey & choose starter\n"
                      "👤 `/profile` - View your trainer profile & progress\n"
                      "🎒 `/party` - Display your current party Pokemon\n"
                      "🏠 `/server` - Get main server invite link",
                inline=False
            )
            embed.add_field(
                name="📊 **Progress & Stats**",
                value="📖 `/pokedex [page]` - Check Pokedex completion progress\n"
                      "📈 `/trainerstats [@user]` - View detailed trainer statistics\n"
                      "🏆 `/leaderboard [category]` - View server leaderboards\n"
                      "🔗 `/invite` - Get bot invite link for other servers",
                inline=False
            )
            embed.set_footer(text="💡 Pro tip: Use /profile to track your journey progress!")
            
        elif category.lower() == "pokemon":
            embed = discord.Embed(
                title="🎒 Pokemon Management", 
                description="Manage your Pokemon collection, party, and PC storage!",
                color=0xff6b6b
            )
            embed.add_field(
                name="🎯 **Catching & Spawning**",
                value="⚾ `/catch [pokeball]` - Catch wild Pokemon that spawn\n"
                      "📍 `/setspawn` - Set monitor/spawn channels (Admin only)\n"
                      "🎾 `/defaultpokeball [type]` - Set your default Pokeball type",
                inline=False
            )
            embed.add_field(
                name="💾 **Storage & Organization**",
                value="📦 `/pokebox [page]` - Browse Pokemon stored in PC\n"
                      "📥 `/deposit [position]` - Move Pokemon from party to PC\n"
                      "📤 `/withdraw [pokemon_id]` - Move Pokemon from PC to party\n"
                      "🔄 `/switch [pos1] [pos2]` - Reorder party positions",
                inline=False
            )
            embed.add_field(
                name="📊 **Pokemon Info & Training**",
                value="📋 `/stats [position]` - View Pokemon stats, moves & IVs\n"
                      "🎓 `/teach [position] [tm/hm]` - Teach TM/HM moves to Pokemon\n"
                      "🎯 `/choosemove` - Choose move to replace when learning new\n"
                      "❌ `/forgetmove` - Skip learning new move\n"
                      "💿 Available: TM01-TM50, HM01-HM05",
                inline=False
            )
            embed.set_footer(text="💡 Tip: Pokemon spawn every 10-20 messages in spawn channels!")
            
        elif category.lower() == "battle":
            embed = discord.Embed(
                title="⚔️ Battle System",
                description="Challenge other trainers to Pokemon battles!",
                color=0xf39c12
            )
            embed.add_field(
                name="🥊 **Player vs Player**",
                value="⚔️ `/battle @user` - Challenge another trainer to battle",
                inline=False
            )
            embed.set_footer(text="💡 Tip: Type advantages can make or break battles!")
            
        elif category.lower() == "economy":
            embed = discord.Embed(
                title="🛒 Economy & Items", 
                description="Manage your money, buy items, and heal your Pokemon!",
                color=0x2ecc71
            )
            embed.add_field(
                name="🏪 **Shopping System**",
                value="🛍️ `/shop` - View available items and prices\n"
                      "💳 `/buy [item] [quantity]` - Purchase items from shop\n"
                      "🎒 `/inventory` - View your current items & quantities\n"
                      "💊 `/use [item] [position]` - Use healing items on Pokemon\n"
                      "🏥 `/healall` - Heal all Pokemon in your party to full HP",
                inline=False
            )

            embed.set_footer(text="💡 Tip: Earn money by battling and daily message activity!")
            
        elif category.lower() == "gym":
            embed = discord.Embed(
                title="🏆 Gym Challenges", 
                description="Battle your way through the Pokemon League to become Champion!",
                color=0x9b59b6
            )
            embed.add_field(
                name="🏛️ **Gym Leaders (8 Badges)**",
                value="🪨 `/gym brock` - Brock (Rock-type)\n"
                      "💧 `/gym misty` - Misty (Water-type)\n"
                      "⚡ `/gym surge` - Lt. Surge (Electric-type)\n"
                      "🌿 `/gym erika` - Erika (Grass-type)\n"
                      "☠️ `/gym koga` - Koga (Poison-type)\n"
                      "🔮 `/gym sabrina` - Sabrina (Psychic-type)\n"
                      "🔥 `/gym blaine` - Blaine (Fire-type)\n"
                      "🌍 `/gym giovanni` - Giovanni (Ground-type)",
                inline=False
            )
            embed.add_field(
                name="⭐ **Elite Four & Champion**",
                value="❄️ `/elite4 lorelei` - Lorelei (Ice-type)\n"
                      "👊 `/elite4 bruno` - Bruno (Fighting-type)\n"
                      "👻 `/elite4 agatha` - Agatha (Ghost-type)\n"
                      "🐉 `/elite4 lance` - Lance (Dragon-type)\n"
                      "👑 `/champion` - Challenge the Champion!",
                inline=False
            )

            embed.set_footer(text="💡 Tip: You need all 8 badges to challenge the Elite Four!")
            
        elif category.lower() == "trading":
            embed = discord.Embed(
                title="🔄 Trading System", 
                description="Trade Pokemon with other trainers and trigger special evolutions!",
                color=0x8e44ad
            )
            embed.add_field(
                name="🤝 **Trading Commands**",
                value="🔄 `/trade @user [your_pos] [their_pos]` - Offer Pokemon trade\n"
                      "📋 `/trades` - View your active trade requests\n"
                      "📍 Uses party positions (1-6) for both trainers",
                inline=False
            )
            embed.add_field(
                name="✨ **Trade Evolutions**",
                value="🧙 **Kadabra** → **Alakazam** (when traded)\n"
                      "💪 **Machoke** → **Machamp** (when traded)\n"
                      "👻 **Haunter** → **Gengar** (when traded)\n"
                      "🪨 **Graveler** → **Golem** (when traded)",
                inline=False
            )
            embed.add_field(
                name="⚠️ **Trading Rules**",
                value="🚫 Cannot trade your last Pokemon\n"
                      "🔒 Pokemon moved to PC after trade\n"
                      "⚡ Evolution triggers automatically\n"
                      "⏰ Trade requests expire after 5 minutes",
                inline=False
            )
            embed.set_footer(text="💡 Tip: Some Pokemon can only evolve through trading!")
            
        elif category.lower() == "admin":
            if not self.is_admin(interaction.user.id):
                embed = discord.Embed(
                    title="🚫 Access Denied",
                    description="⚠️ **This command can only be used by Professor Byte's administrator.**\n\n"
                               "🔒 Admin commands are restricted to maintain fair gameplay.",
                    color=0xe74c3c
                )
                embed.set_footer(text="💡 Contact Professor Byte's owner if you need admin assistance!")
            else:
                embed = discord.Embed(
                    title="⚙️ Admin Commands", 
                    description="🛠️ **Administrator-only commands for Professor Byte management**",
                    color=0xe74c3c
                )
                embed.add_field(
                    name="🎮 **Pokemon Management**",
                    value="🌟 `/spawn [pokemon] [level] [shiny]` - Force spawn specific Pokemon\n"
                          "📈 `/setlevel @user [pokemon_id] [level]` - Set Pokemon level (1-100)\n"
                          "🗑️ `/resetuser @user` - Reset user progress completely",
                    inline=False
                )
                embed.add_field(
                    name="💰 **Economy Management**",
                    value="💵 `/givemoney @user [amount]` - Give money to user\n"
                          "🎁 `/giveitem @user [item] [quantity]` - Give items to user\n"
                          "📍 `/setspawn` - Configure monitor/spawn channels",
                    inline=False
                )
                embed.set_footer(text="⚠️ Use admin commands responsibly!")
            
        else:
            embed = discord.Embed(
                title="❌ Invalid Category",
                description="🤔 **That category doesn't exist!**\n\n"
                           "📚 **Available categories:**\n"
                           "• `basic` - Getting started & profiles\n"
                           "• `pokemon` - Pokemon management\n"
                           "• `battle` - Battle system\n"
                           "• `economy` - Shop & items\n"
                           "• `gym` - Gym challenges\n"
                           "• `trading` - Trading system\n"
                           "• `admin` - Admin commands",
                color=0xe74c3c
            )
            embed.set_footer(text="💡 Use /help [category] to view specific commands!")
            
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpSystem(bot))