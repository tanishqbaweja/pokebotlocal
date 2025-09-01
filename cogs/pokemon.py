import discord
from discord.ext import commands
from discord import app_commands
import math

class Pokemon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="pokebox", description="View your Pokemon storage")
    async def pokebox(self, interaction: discord.Interaction, page: int = 1):
        user_id = interaction.user.id
        
        # Get all Pokemon not in party
        pokemon_list = await self.bot.db.get_user_pokemon(user_id, in_party=False)
        
        if not pokemon_list:
            await interaction.response.send_message("Your PC box is empty!", ephemeral=True)
            return
            
        # Pagination
        per_page = 10
        total_pages = math.ceil(len(pokemon_list) / per_page)
        page = max(1, min(page, total_pages))
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_pokemon = pokemon_list[start_idx:end_idx]
        
        embed = discord.Embed(
            title=f"PC Box - Page {page}/{total_pages}",
            description=f"Total Pokemon: {len(pokemon_list)}",
            color=0x9b59b6
        )
        
        for pokemon in page_pokemon:
            type_str = pokemon['type1']
            if pokemon['type2']:
                type_str += f"/{pokemon['type2']}"
                
            shiny_indicator = "✨ " if pokemon['is_shiny'] else ""
            embed.add_field(
                name=f"#{pokemon['id']} {shiny_indicator}{pokemon['name']}",
                value=f"Level {pokemon['level']} • {type_str}",
                inline=True
            )
        
        if total_pages > 1:
            view = PokeboxView(user_id, page, total_pages)
            await interaction.response.send_message(embed=embed, view=view)
        else:
            await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="deposit", description="Move a Pokemon from party to PC")
    async def deposit(self, interaction: discord.Interaction, position: int):
        user_id = interaction.user.id
        
        if position < 1 or position > 6:
            await interaction.response.send_message("Position must be between 1 and 6!", ephemeral=True)
            return
        
        # Check if Pokemon exists at that party position
        pokemon = await self.bot.db.fetchrow(
            "SELECT * FROM pokemon WHERE owner_id = $1 AND in_party = TRUE AND party_position = $2",
            user_id, position
        )
        
        if not pokemon:
            await interaction.response.send_message(f"No Pokemon at position {position}!", ephemeral=True)
            return
            
        # Check if it's the last Pokemon in party
        party_count = await self.bot.db.fetchval(
            "SELECT COUNT(*) FROM pokemon WHERE owner_id = $1 AND in_party = TRUE",
            user_id
        )
        
        if party_count <= 1:
            await interaction.response.send_message("You can't deposit your last Pokemon!", ephemeral=True)
            return
            
        # Move to PC
        await self.bot.db.execute(
            "UPDATE pokemon SET in_party = FALSE, party_position = NULL WHERE id = $1",
            pokemon['id']
        )
        
        # Reorder party positions
        await self._reorder_party(user_id)
        
        from data.complete_pokemon_data import COMPLETE_POKEMON_DATA
        species = COMPLETE_POKEMON_DATA[pokemon['species_id']]
        
        await interaction.response.send_message(f"Deposited {species['name']} to PC!")
        
    @app_commands.command(name="withdraw", description="Move a Pokemon from PC to party")
    async def withdraw(self, interaction: discord.Interaction, pokemon_id: int):
        user_id = interaction.user.id
        
        # Check if user exists
        user = await self.bot.db.get_user(user_id)
        if not user:
            await interaction.response.send_message("You haven't started your journey yet! Use `/start` to begin.", ephemeral=True)
            return
            
        # Check total Pokemon limit (999)
        total_pokemon = await self.bot.db.fetchval(
            "SELECT COUNT(*) FROM pokemon WHERE owner_id = $1",
            user_id
        )
        
        if total_pokemon >= 999:
            await interaction.response.send_message("You've reached the maximum Pokemon limit (999)!", ephemeral=True)
            return
        
        # Check if Pokemon exists and is in PC
        pokemon = await self.bot.db.fetchrow(
            "SELECT * FROM pokemon WHERE id = $1 AND owner_id = $2 AND in_party = FALSE",
            pokemon_id, user_id
        )
        
        if not pokemon:
            await interaction.response.send_message("Pokemon not found in your PC!", ephemeral=True)
            return
            
        # Check party space
        party_count = await self.bot.db.fetchval(
            "SELECT COUNT(*) FROM pokemon WHERE owner_id = $1 AND in_party = TRUE",
            user_id
        )
        
        if party_count >= 6:
            await interaction.response.send_message("Your party is full! Deposit a Pokemon first.", ephemeral=True)
            return
            
        # Move to party
        await self.bot.db.execute(
            "UPDATE pokemon SET in_party = TRUE, party_position = $1 WHERE id = $2",
            party_count + 1, pokemon_id
        )
        
        from data.complete_pokemon_data import COMPLETE_POKEMON_DATA
        species = COMPLETE_POKEMON_DATA[pokemon['species_id']]
        
        await interaction.response.send_message(f"Withdrew {species['name']} to party!")
        
    @app_commands.command(name="stats", description="View a Pokemon's stats and moves")
    async def stats(self, interaction: discord.Interaction, position: int):
        user_id = interaction.user.id
        
        if position < 1 or position > 6:
            await interaction.response.send_message("Position must be between 1 and 6!", ephemeral=True)
            return
        
        pokemon = await self.bot.db.fetchrow(
            "SELECT * FROM pokemon WHERE owner_id = $1 AND in_party = TRUE AND party_position = $2",
            user_id, position
        )
        
        if not pokemon:
            await interaction.response.send_message(f"No Pokemon at position {position}!", ephemeral=True)
            return
            
        from data.complete_pokemon_data import COMPLETE_POKEMON_DATA
        species = COMPLETE_POKEMON_DATA[pokemon['species_id']]
        
        embed = discord.Embed(
            title=f"{species['name']}'s Stats & Moves",
            color=0xe67e22
        )
        
        # Add IV display with exact numbers
        embed.add_field(
            name="IVs (Individual Values)", 
            value=f"HP: {pokemon['hp_iv']}/15\n"
                  f"Attack: {pokemon['attack_iv']}/15\n"
                  f"Defense: {pokemon['defense_iv']}/15\n"
                  f"Special: {pokemon['special_iv']}/15\n"
                  f"Speed: {pokemon['speed_iv']}/15",
            inline=True
        )
        
        moves = [pokemon['move1'], pokemon['move2'], pokemon['move3'], pokemon['move4']]
        move_list = [move for move in moves if move]
        
        if not move_list:
            embed.add_field(name="Moves", value="This Pokemon doesn't know any moves yet!", inline=False)
        else:
            move_text = "\n".join([f"{i}. {move.replace('_', ' ').title()}" for i, move in enumerate(move_list, 1)])
            embed.add_field(name="Moves", value=move_text, inline=False)
                
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="switch", description="Switch positions of two Pokemon in party")
    async def switch_positions(self, interaction: discord.Interaction, position1: int, position2: int):
        user_id = interaction.user.id
        
        if position1 < 1 or position1 > 6 or position2 < 1 or position2 > 6:
            await interaction.response.send_message("Positions must be between 1 and 6!", ephemeral=True)
            return
            
        if position1 == position2:
            await interaction.response.send_message("Can't switch a Pokemon with itself!", ephemeral=True)
            return
            
        # Get Pokemon at both positions in single query for better performance
        pokemon_data = await self.bot.db.fetch(
            "SELECT * FROM pokemon WHERE owner_id = $1 AND in_party = TRUE AND party_position IN ($2, $3)",
            user_id, position1, position2
        )
        
        pokemon1 = next((p for p in pokemon_data if p['party_position'] == position1), None)
        pokemon2 = next((p for p in pokemon_data if p['party_position'] == position2), None)
        
        if not pokemon1:
            await interaction.response.send_message(f"No Pokemon at position {position1}!", ephemeral=True)
            return
            
        if not pokemon2:
            await interaction.response.send_message(f"No Pokemon at position {position2}!", ephemeral=True)
            return
            
        # Switch positions
        await self.bot.db.execute(
            "UPDATE pokemon SET party_position = $1 WHERE id = $2",
            position2, pokemon1['id']
        )
        await self.bot.db.execute(
            "UPDATE pokemon SET party_position = $1 WHERE id = $2",
            position1, pokemon2['id']
        )
        
        from data.complete_pokemon_data import COMPLETE_POKEMON_DATA
        species1 = COMPLETE_POKEMON_DATA[pokemon1['species_id']]
        species2 = COMPLETE_POKEMON_DATA[pokemon2['species_id']]
        
        await interaction.response.send_message(
            f"Switched {species1['name']} (pos {position1}) with {species2['name']} (pos {position2})!"
        )
        
    async def _reorder_party(self, user_id):
        """Reorder party positions after deposit"""
        party_pokemon = await self.bot.db.fetch(
            "SELECT id FROM pokemon WHERE owner_id = $1 AND in_party = TRUE ORDER BY party_position",
            user_id
        )
        
        # Batch update party positions for better performance
        if party_pokemon:
            update_values = [(i, pokemon['id']) for i, pokemon in enumerate(party_pokemon, 1)]
            for position, pokemon_id in update_values:
                await self.bot.db.execute(
                    "UPDATE pokemon SET party_position = $1 WHERE id = $2",
                    position, pokemon_id
                )

class PokeboxView(discord.ui.View):
    def __init__(self, user_id, current_page, total_pages):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.current_page = current_page
        self.total_pages = total_pages
        
        # Add buttons based on current page
        if current_page > 1:
            self.add_item(discord.ui.Button(label="First Page", custom_id="first", style=discord.ButtonStyle.secondary))
            self.add_item(discord.ui.Button(label="Previous Page", custom_id="prev", style=discord.ButtonStyle.primary))
        
        if current_page < total_pages:
            self.add_item(discord.ui.Button(label="Next Page", custom_id="next", style=discord.ButtonStyle.primary))
            self.add_item(discord.ui.Button(label="Last Page", custom_id="last", style=discord.ButtonStyle.secondary))
            
        # Set callbacks
        for item in self.children:
            if item.custom_id == "first":
                item.callback = self.first_page
            elif item.custom_id == "prev":
                item.callback = self.prev_page
            elif item.custom_id == "next":
                item.callback = self.next_page
            elif item.custom_id == "last":
                item.callback = self.last_page
                
    async def first_page(self, interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your pokebox!", ephemeral=True)
            return
        await self.update_page(interaction, 1)
        
    async def prev_page(self, interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your pokebox!", ephemeral=True)
            return
        await self.update_page(interaction, self.current_page - 1)
        
    async def next_page(self, interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your pokebox!", ephemeral=True)
            return
        await self.update_page(interaction, self.current_page + 1)
        
    async def last_page(self, interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your pokebox!", ephemeral=True)
            return
        await self.update_page(interaction, self.total_pages)
        
    async def update_page(self, interaction, new_page):
        # Get Pokemon data for new page
        pokemon_list = await interaction.client.db.get_user_pokemon(self.user_id, in_party=False)
        
        per_page = 10
        start_idx = (new_page - 1) * per_page
        end_idx = start_idx + per_page
        page_pokemon = pokemon_list[start_idx:end_idx]
        
        embed = discord.Embed(
            title=f"PC Box - Page {new_page}/{self.total_pages}",
            description=f"Total Pokemon: {len(pokemon_list)}",
            color=0x9b59b6
        )
        
        for pokemon in page_pokemon:
            type_str = pokemon['type1']
            if pokemon['type2']:
                type_str += f"/{pokemon['type2']}"
                
            shiny_indicator = "✨ " if pokemon['is_shiny'] else ""
            embed.add_field(
                name=f"#{pokemon['id']} {shiny_indicator}{pokemon['name']}",
                value=f"Level {pokemon['level']} • {type_str}",
                inline=True
            )
        
        # Create new view with updated page
        new_view = PokeboxView(self.user_id, new_page, self.total_pages)
        await interaction.response.edit_message(embed=embed, view=new_view)

async def setup(bot):
    await bot.add_cog(Pokemon(bot))