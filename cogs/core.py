import discord
from discord.ext import commands
from discord import app_commands

class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="start", description="Begin your Pokemon journey!")
    async def start(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        username = interaction.user.display_name
        
        # Check if user already exists
        existing_user = await self.bot.db.get_user(user_id)
        if existing_user:
            await interaction.response.send_message("You've already started your journey!", ephemeral=True)
            return
            
        # Create new user with starter money
        await self.bot.db.execute(
            "INSERT INTO users (user_id, username, money) VALUES ($1, $2, $3)",
            user_id, username, 15000
        )
        
        # Give starter pokeballs
        starter_items = [
            ("pokeball", 30),
            ("greatball", 15), 
            ("ultraball", 8),
            ("masterball", 1)
        ]
        
        for item_name, quantity in starter_items:
            await self.bot.db.execute(
                "INSERT INTO user_inventory (user_id, item_name, quantity) VALUES ($1, $2, $3)",
                user_id, item_name, quantity
            )
        
        # Starter selection view
        view = StarterView(self.bot.db, user_id)
        embed = discord.Embed(
            title="Choose Your Starter Pokemon!",
            description="Select your first Pokemon to begin your adventure:",
            color=0x00ff00
        )
        embed.add_field(name="🌱 Bulbasaur", value="Grass/Poison Type", inline=True)
        embed.add_field(name="🔥 Charmander", value="Fire Type", inline=True)
        embed.add_field(name="💧 Squirtle", value="Water Type", inline=True)
        
        await interaction.response.send_message(embed=embed, view=view)
        
    @app_commands.command(name="profile", description="View your trainer profile")
    async def profile(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user = await self.bot.db.get_user(user_id)
        
        if not user:
            await interaction.response.send_message("You haven't started your journey yet! Use `/start` to begin.", ephemeral=True)
            return
            
        party = await self.bot.db.get_user_pokemon(user_id, in_party=True)
        
        # Calculate progress
        gym_badges = min(user['badges'], 8)
        elite_four = max(0, min(user['badges'] - 8, 4))
        champion = 1 if user['badges'] >= 13 else 0
        
        embed = discord.Embed(
            title=f"Trainer {user['username']}",
            color=0x3498db
        )
        embed.add_field(name="💰 Money", value=f"{user['money']:,} rupees", inline=True)
        embed.add_field(name="🏆 Gym Badges", value=f"{gym_badges}/8", inline=True)
        embed.add_field(name="⭐ Elite Four", value=f"{elite_four}/4", inline=True)
        embed.add_field(name="👑 Champion", value=f"{champion}/1", inline=True)
        embed.add_field(name="🎒 Party", value=f"{len(party)}/6 Pokemon", inline=True)
        
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="server", description="Get the main server invite")
    async def server(self, interaction: discord.Interaction):
        try:
            await interaction.user.send("Join the main Professor Byte server: https://discord.gg/fH7JxycRjA")
            await interaction.response.send_message("Server invite sent to your DMs!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I couldn't send you a DM! Here's the server link: https://discord.gg/fH7JxycRjA", ephemeral=True)
        except Exception:
            await interaction.response.send_message("Main server: https://discord.gg/fH7JxycRjA", ephemeral=True)
        
    @app_commands.command(name="party", description="View your current party")
    async def party(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        party = await self.bot.db.get_user_pokemon(user_id, in_party=True)
        
        if not party:
            await interaction.response.send_message("Your party is empty! Catch some Pokemon first.", ephemeral=True)
            return
            
        embed = discord.Embed(title="Your Party", color=0xe74c3c)
        
        # Fix party positions if needed
        pokemon_cog = self.bot.get_cog('Pokemon')
        if pokemon_cog:
            await pokemon_cog._reorder_party(user_id)
            # Refresh party data after reordering
            party = await self.bot.db.get_user_pokemon(user_id, in_party=True)
        
        for i, pokemon in enumerate(party, 1):
            type_str = pokemon['type1']
            if pokemon['type2']:
                type_str += f"/{pokemon['type2']}"
                
            shiny_indicator = "✨ " if pokemon['is_shiny'] else ""
            
            field_value = f"Level {pokemon['level']} • {type_str}\nHP: {pokemon['current_hp']}/{self._calculate_max_hp(pokemon)}"
                
            embed.add_field(
                name=f"{i}. {shiny_indicator}{pokemon['name']}",
                value=field_value,
                inline=False
            )
            
        await interaction.response.send_message(embed=embed)
        
    def _calculate_max_hp(self, pokemon):
        from data.complete_pokemon_data import COMPLETE_POKEMON_DATA
        species = COMPLETE_POKEMON_DATA[pokemon['species_id']]
        return ((species['base_hp'] + pokemon['hp_iv']) * 2 * pokemon['level'] // 100) + pokemon['level'] + 10

class StarterView(discord.ui.View):
    def __init__(self, db, user_id):
        super().__init__(timeout=60)
        self.db = db
        self.user_id = user_id
        
    @discord.ui.button(label="Bulbasaur", style=discord.ButtonStyle.green, emoji="🌱")
    async def bulbasaur(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._choose_starter(interaction, 1, "Bulbasaur")
        
    @discord.ui.button(label="Charmander", style=discord.ButtonStyle.red, emoji="🔥")
    async def charmander(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._choose_starter(interaction, 4, "Charmander")
        
    @discord.ui.button(label="Squirtle", style=discord.ButtonStyle.blurple, emoji="💧")
    async def squirtle(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._choose_starter(interaction, 7, "Squirtle")
        
    async def _choose_starter(self, interaction, species_id, name):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your starter selection!", ephemeral=True)
            return
            
        try:
            pokemon_id = await self.db.add_pokemon(self.user_id, species_id, level=5)
        except Exception as e:
            import logging
            logging.exception(f"Failed to add starter Pokemon: {e}")
            await interaction.response.send_message("Failed to add starter Pokemon. Please try again.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="Congratulations!",
            description=f"You chose {name} as your starter Pokemon!",
            color=0x00ff00
        )
        embed.add_field(name="Level", value="5", inline=True)
        embed.add_field(
            name="Starter Items Received",
            value="💰 15,000 rupees\n⚾ 30 Pokeballs\n🔵 15 Great Balls\n🟡 8 Ultra Balls\n🟣 1 Master Ball",
            inline=False
        )
        
        self.clear_items()
        await interaction.response.edit_message(embed=embed, view=self)

async def setup(bot):
    await bot.add_cog(Core(bot))