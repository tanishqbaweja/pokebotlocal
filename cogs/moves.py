import discord
from discord.ext import commands
from discord import app_commands
from data.complete_moves_data import TM_MOVES, HM_MOVES, COMPLETE_MOVES_DATA
from data.tm_hm_compatibility import get_learnable_tms_hms

class Moves(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="teach", description="Teach a TM or HM move to a Pokemon")
    async def teach(self, interaction: discord.Interaction, position: int, move_item: str):
        user_id = interaction.user.id
        move_item = move_item.lower()
        
        if position < 1 or position > 6:
            await interaction.response.send_message("Position must be between 1 and 6!", ephemeral=True)
            return
        
        # Check if user has the TM/HM
        inventory = await self.bot.db.fetchrow(
            "SELECT quantity FROM user_inventory WHERE user_id = $1 AND item_name = $2",
            user_id, move_item
        )
        
        if not inventory or inventory['quantity'] <= 0:
            await interaction.response.send_message(f"You don't have {move_item.upper()}!", ephemeral=True)
            return
            
        # Get move name
        move_name = None
        if move_item in TM_MOVES:
            move_name = TM_MOVES[move_item]
        elif move_item in HM_MOVES:
            move_name = HM_MOVES[move_item]
        else:
            await interaction.response.send_message("Invalid TM/HM!", ephemeral=True)
            return
            
        # Get Pokemon from party position
        pokemon = await self.bot.db.fetchrow(
            "SELECT * FROM pokemon WHERE owner_id = $1 AND in_party = TRUE AND party_position = $2",
            user_id, position
        )
        
        if not pokemon:
            await interaction.response.send_message(f"No Pokemon at position {position}!", ephemeral=True)
            return
            
        # Check if Pokemon can learn this TM/HM
        from data.complete_pokemon_data import COMPLETE_POKEMON_DATA
        species = COMPLETE_POKEMON_DATA[pokemon['species_id']]
        learnable_moves = get_learnable_tms_hms(pokemon['species_id'])
        
        if move_item not in learnable_moves:
            await interaction.response.send_message(f"{species['name']} cannot learn {move_item.upper()}!", ephemeral=True)
            return
            
        # Check if Pokemon already knows the move
        current_moves = [pokemon.get('move1'), pokemon.get('move2'), pokemon.get('move3'), pokemon.get('move4')]
        if move_name in current_moves:
            await interaction.response.send_message(f"{species['name']} already knows {move_name.replace('_', ' ').title()}!", ephemeral=True)
            return
            
        # Find empty slot or ask to replace
        empty_slot = None
        for i in range(4):
            if not current_moves[i]:
                empty_slot = i + 1
                break
                
        if empty_slot:
            # Teach to empty slot - validate slot number for security
            if empty_slot not in [1, 2, 3, 4]:
                await interaction.response.send_message("Invalid move slot!", ephemeral=True)
                return
            
            column_map = {1: 'move1', 2: 'move2', 3: 'move3', 4: 'move4'}
            await self.bot.db.execute(
                f"UPDATE pokemon SET {column_map[empty_slot]} = $1 WHERE id = $2",
                move_name, pokemon['id']
            )
            
            # Remove TM (HMs are reusable)
            if move_item.startswith('tm'):
                await self.bot.db.execute(
                    "UPDATE user_inventory SET quantity = quantity - 1 WHERE user_id = $1 AND item_name = $2",
                    user_id, move_item
                )
                
            from data.complete_pokemon_data import COMPLETE_POKEMON_DATA
            species = COMPLETE_POKEMON_DATA[pokemon['species_id']]
            await interaction.response.send_message(f"{species['name']} learned {move_name.replace('_', ' ').title()}!")
        else:
            # All slots full - show replacement view
            view = MoveReplaceView(self.bot, pokemon, move_name, move_item, user_id)
            from data.complete_pokemon_data import COMPLETE_POKEMON_DATA
            species = COMPLETE_POKEMON_DATA[pokemon['species_id']]
            
            embed = discord.Embed(
                title="Move Replacement",
                description=f"{species['name']} wants to learn {move_name.replace('_', ' ').title()}, but already knows 4 moves!",
                color=0xf39c12
            )
            
            for i, move in enumerate(current_moves, 1):
                embed.add_field(name=f"Move {i}", value=move.replace('_', ' ').title(), inline=True)
                
            await interaction.response.send_message(embed=embed, view=view)
            


class MoveReplaceView(discord.ui.View):
    def __init__(self, bot, pokemon, new_move, move_item, user_id):
        super().__init__(timeout=60)
        self.bot = bot
        self.pokemon = pokemon
        self.new_move = new_move
        self.move_item = move_item
        self.user_id = user_id
        
        # Add buttons for each move
        moves = [pokemon.get('move1'), pokemon.get('move2'), pokemon.get('move3'), pokemon.get('move4')]
        for i, move in enumerate(moves, 1):
            button = discord.ui.Button(label=f"Replace {move.replace('_', ' ').title()}", custom_id=f"replace_{i}")
            button.callback = self._create_replace_callback(i)
            self.add_item(button)
            
        # Add cancel button
        cancel_button = discord.ui.Button(label="Don't Learn", style=discord.ButtonStyle.red, custom_id="cancel")
        cancel_button.callback = self._cancel
        self.add_item(cancel_button)
        
    def _create_replace_callback(self, move_slot):
        async def callback(interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("Not your Pokemon!", ephemeral=True)
                return
                
            # Replace the move - validate slot number for security
            if move_slot not in [1, 2, 3, 4]:
                await interaction.response.send_message("Invalid move slot!", ephemeral=True)
                return
                
            column_map = {1: 'move1', 2: 'move2', 3: 'move3', 4: 'move4'}
            await self.bot.db.execute(
                f"UPDATE pokemon SET {column_map[move_slot]} = $1 WHERE id = $2",
                self.new_move, self.pokemon['id']
            )
            
            # Remove TM (HMs are reusable)
            if self.move_item.startswith('tm'):
                await self.bot.db.execute(
                    "UPDATE user_inventory SET quantity = quantity - 1 WHERE user_id = $1 AND item_name = $2",
                    self.user_id, self.move_item
                )
                
            from data.complete_pokemon_data import COMPLETE_POKEMON_DATA
            species = COMPLETE_POKEMON_DATA[self.pokemon['species_id']]
            old_move = self.pokemon.get(f'move{move_slot}', 'Unknown Move')
            
            self.clear_items()
            await interaction.response.edit_message(
                content=f"{species['name']} forgot {old_move.replace('_', ' ').title()} and learned {self.new_move.replace('_', ' ').title()}!",
                embed=None, view=self
            )
            
        return callback
        
    async def _cancel(self, interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Not your Pokemon!", ephemeral=True)
            return
            
        from data.complete_pokemon_data import COMPLETE_POKEMON_DATA
        species = COMPLETE_POKEMON_DATA[self.pokemon['species_id']]
        
        self.clear_items()
        await interaction.response.edit_message(
            content=f"{species['name']} did not learn {self.new_move.replace('_', ' ').title()}.",
            embed=None, view=self
        )

async def setup(bot):
    await bot.add_cog(Moves(bot))