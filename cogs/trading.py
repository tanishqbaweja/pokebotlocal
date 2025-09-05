import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime, timedelta

class Trading(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="trade", description="Offer a trade to another user")
    async def trade(self, interaction: discord.Interaction, user: discord.Member, your_position: int, their_position: int):
        requester_id = interaction.user.id
        target_id = user.id
        
        if requester_id == target_id:
            await interaction.response.send_message("You can't trade with yourself!", ephemeral=True)
            return
            
        # Check for pending move learning
        move_learning_cog = self.bot.get_cog('MoveLearning')
        if move_learning_cog:
            if move_learning_cog.has_pending_moves(requester_id):
                await interaction.response.send_message("You have a Pokemon waiting to learn a move! Use `/choosemove` or `/forgetmove` first.", ephemeral=True)
                return
            if move_learning_cog.has_pending_moves(target_id):
                await interaction.response.send_message(f"{user.mention} has a Pokemon waiting to learn a move and cannot trade right now.", ephemeral=True)
                return
            
        if your_position < 1 or your_position > 6 or their_position < 1 or their_position > 6:
            await interaction.response.send_message("Positions must be between 1 and 6!", ephemeral=True)
            return
            
        # Get both Pokemon from party positions
        your_pokemon = await self.bot.db.fetchrow(
            "SELECT * FROM pokemon WHERE owner_id = $1 AND in_party = TRUE AND party_position = $2",
            requester_id, your_position
        )
        
        their_pokemon = await self.bot.db.fetchrow(
            "SELECT * FROM pokemon WHERE owner_id = $1 AND in_party = TRUE AND party_position = $2",
            target_id, their_position
        )
        
        if not your_pokemon:
            await interaction.response.send_message(f"No Pokemon at position {your_position} in your party!", ephemeral=True)
            return
            
        if not their_pokemon:
            await interaction.response.send_message(f"{user.display_name} has no Pokemon at position {their_position}!", ephemeral=True)
            return
            
        # Check for existing active trades
        existing = await self.bot.db.fetchrow(
            "SELECT * FROM trades WHERE (requester_id = $1 OR target_id = $1) AND status = 'pending'",
            requester_id
        )
        
        if existing:
            await interaction.response.send_message("You already have an active trade request!", ephemeral=True)
            return
            
        from data.complete_pokemon_data import COMPLETE_POKEMON_DATA
        your_species = COMPLETE_POKEMON_DATA[your_pokemon['species_id']]
        their_species = COMPLETE_POKEMON_DATA[their_pokemon['species_id']]
        
        # Create simple trade confirmation
        embed = discord.Embed(
            title="Trade Proposal",
            description=f"{interaction.user.mention} wants to trade:\n"
                       f"**{your_species['name']}** (Lv.{your_pokemon['level']}) ↔️ **{their_species['name']}** (Lv.{their_pokemon['level']})",
            color=0x3498db
        )
        
        view = SimpleTradeView(self.bot, requester_id, target_id, your_pokemon['id'], their_pokemon['id'])
        await interaction.response.send_message(f"{user.mention}", embed=embed, view=view)
        view.message = await interaction.original_response()
        
    @app_commands.command(name="trades", description="View your active trade requests")
    async def trades(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        
        trades = await self.bot.db.fetch(
            """SELECT t.*, p.species_id, ps.name as pokemon_name, p.level
               FROM trades t
               JOIN pokemon p ON t.pokemon_offered = p.id
               JOIN pokemon_species ps ON p.species_id = ps.id
               WHERE (t.requester_id = $1 OR t.target_id = $1) AND t.status = 'pending'
               AND t.expires_at > NOW()""",
            user_id
        )
        
        if not trades:
            await interaction.response.send_message("No active trades!", ephemeral=True)
            return
            
        embed = discord.Embed(title="Active Trades", color=0x9b59b6)
        
        for trade in trades:
            if trade['requester_id'] == user_id:
                embed.add_field(
                    name=f"Outgoing Trade #{trade['id']}",
                    value=f"Offering: {trade['pokemon_name']} (Lv.{trade['level']})\nTo: <@{trade['target_id']}>",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"Incoming Trade #{trade['id']}",
                    value=f"Receiving: {trade['pokemon_name']} (Lv.{trade['level']})\nFrom: <@{trade['requester_id']}>",
                    inline=False
                )
                
        await interaction.response.send_message(embed=embed)
        
    async def accept_trade(self, trade_id, target_pokemon_id, user_id):
        # Get trade details
        trade = await self.bot.db.fetchrow(
            "SELECT * FROM trades WHERE id = $1 AND status = 'pending' AND expires_at > NOW()",
            trade_id
        )
        
        if not trade or trade['target_id'] != user_id:
            return "Trade not found or expired!"
            
        # Validate target Pokemon
        target_pokemon = await self.bot.db.fetchrow(
            "SELECT * FROM pokemon WHERE id = $1 AND owner_id = $2",
            target_pokemon_id, user_id
        )
        
        if not target_pokemon:
            return "Pokemon not found or doesn't belong to you!"
            
        if target_pokemon['in_party'] and await self._get_party_count(user_id) <= 1:
            return "You can't trade your last Pokemon!"
            
        # Execute trade
        await self.bot.db.execute("BEGIN")
        
        try:
            # Swap ownership
            await self.bot.db.execute(
                "UPDATE pokemon SET owner_id = $1, in_party = FALSE, party_position = NULL WHERE id = $2",
                user_id, trade['pokemon_offered']
            )
            
            await self.bot.db.execute(
                "UPDATE pokemon SET owner_id = $1, in_party = FALSE, party_position = NULL WHERE id = $2",
                trade['requester_id'], target_pokemon_id
            )
            
            # Update trade status
            await self.bot.db.execute(
                "UPDATE trades SET status = 'completed', pokemon_requested = $1 WHERE id = $2",
                target_pokemon_id, trade_id
            )
            
            # Check for evolution trades
            await self._check_trade_evolution(trade['pokemon_offered'])
            await self._check_trade_evolution(target_pokemon_id)
            
            await self.bot.db.execute("COMMIT")
            return "Trade completed successfully!"
            
        except Exception as e:
            await self.bot.db.execute("ROLLBACK")
            return f"Trade failed: {str(e)}"
            
    # Trade evolution mapping as class constant
    TRADE_EVOLUTIONS = {
        64: 65,   # Kadabra -> Alakazam
        67: 68,   # Machoke -> Machamp
        93: 94,   # Haunter -> Gengar
        75: 76    # Graveler -> Golem
    }
    
    async def _check_trade_evolution(self, pokemon_id):
        # Get Pokemon data
        pokemon = await self.bot.db.fetchrow("SELECT * FROM pokemon WHERE id = $1", pokemon_id)
        if not pokemon:
            return
            
        species_id = pokemon['species_id']
        if species_id in self.TRADE_EVOLUTIONS:
            new_species = self.TRADE_EVOLUTIONS[species_id]
            
            # Evolve Pokemon
            await self.bot.db.execute(
                "UPDATE pokemon SET species_id = $1 WHERE id = $2",
                new_species, pokemon_id
            )
            
            # Recalculate HP for new species
            from data.complete_pokemon_data import COMPLETE_POKEMON_DATA
            new_species_data = COMPLETE_POKEMON_DATA[new_species]
            old_species_data = COMPLETE_POKEMON_DATA[species_id]
            old_max_hp = ((old_species_data['base_hp'] + pokemon['hp_iv']) * 2 * pokemon['level'] // 100) + pokemon['level'] + 10
            new_max_hp = ((new_species_data['base_hp'] + pokemon['hp_iv']) * 2 * pokemon['level'] // 100) + pokemon['level'] + 10
            
            # Calculate proportional HP (maintain HP percentage)
            hp_percentage = pokemon['current_hp'] / old_max_hp
            new_current_hp = int(new_max_hp * hp_percentage)
            new_current_hp = max(1, new_current_hp)  # Ensure at least 1 HP
            
            if new_current_hp != pokemon['current_hp']:
                await self.bot.db.execute(
                    "UPDATE pokemon SET current_hp = $1 WHERE id = $2",
                    new_current_hp, pokemon_id
                )
            
            # Log evolution for potential notification
            old_name = COMPLETE_POKEMON_DATA[species_id]['name']
            new_name = new_species_data['name']
            import logging
            logging.info(f"Trade evolution: {old_name} -> {new_name} (Pokemon ID: {pokemon_id})")
            
            # Send evolution notification to owner
            try:
                user_obj = self.bot.get_user(pokemon['owner_id'])
                if user_obj:
                    embed = discord.Embed(
                        title="Trade Evolution!",
                        description=f"Your {old_name} evolved into {new_name} through trading!",
                        color=0xffd700
                    )
                    await user_obj.send(embed=embed)
            except Exception as e:
                logging.info(f"Could not send trade evolution DM to user {pokemon['owner_id']}: {e}")
            
    async def _get_party_count(self, user_id):
        return await self.bot.db.fetchval(
            "SELECT COUNT(*) FROM pokemon WHERE owner_id = $1 AND in_party = TRUE",
            user_id
        )

class SimpleTradeView(discord.ui.View):
    def __init__(self, bot, requester_id, target_id, pokemon1_id, pokemon2_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.requester_id = requester_id
        self.target_id = target_id
        self.pokemon1_id = pokemon1_id
        self.pokemon2_id = pokemon2_id
        self.message = None
        
    async def on_timeout(self):
        embed = discord.Embed(
            title="Trade Expired",
            description="This trade request has expired.",
            color=0x808080
        )
        self.clear_items()
        if self.message:
            try:
                await self.message.edit(embed=embed, view=self)
            except (discord.HTTPException, discord.NotFound, discord.Forbidden) as e:
                import logging
                logging.warning(f"Failed to edit message after timeout: {e}")
        
    @discord.ui.button(label="Accept Trade", style=discord.ButtonStyle.green)
    async def accept_trade(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target_id:
            await interaction.response.send_message("This trade isn't for you!", ephemeral=True)
            return
            
        # Check for pending move learning
        move_learning_cog = self.bot.get_cog('MoveLearning')
        if move_learning_cog:
            if move_learning_cog.has_pending_moves(self.requester_id):
                await interaction.response.send_message("The other trainer has a Pokemon waiting to learn a move!", ephemeral=True)
                return
            if move_learning_cog.has_pending_moves(self.target_id):
                await interaction.response.send_message("You have a Pokemon waiting to learn a move! Use `/choosemove` or `/forgetmove` first.", ephemeral=True)
                return
                
        # Check party count - can't trade last Pokemon
        target_party_count = await self.bot.db.fetchval(
            "SELECT COUNT(*) FROM pokemon WHERE owner_id = $1 AND in_party = TRUE",
            self.target_id
        )
        
        if target_party_count <= 1:
            await interaction.response.send_message("You can't trade your last Pokemon!", ephemeral=True)
            return
            
        # Execute trade
        try:
            await self.bot.db.execute("BEGIN")
            
            # Swap ownership
            await self.bot.db.execute(
                "UPDATE pokemon SET owner_id = $1, in_party = FALSE, party_position = NULL WHERE id = $2",
                self.target_id, self.pokemon1_id
            )
            
            await self.bot.db.execute(
                "UPDATE pokemon SET owner_id = $1, in_party = FALSE, party_position = NULL WHERE id = $2",
                self.requester_id, self.pokemon2_id
            )
            
            # Reorder party positions for both users
            pokemon_cog = self.bot.get_cog('Pokemon')
            if pokemon_cog:
                await pokemon_cog._reorder_party(self.requester_id)
                await pokemon_cog._reorder_party(self.target_id)
            
            # Check for trade evolution
            trading_cog = self.bot.get_cog('Trading')
            if trading_cog:
                try:
                    await trading_cog._check_trade_evolution(self.pokemon1_id)
                    await trading_cog._check_trade_evolution(self.pokemon2_id)
                except Exception as e:
                    import logging
                    logging.exception(f"Trade evolution error: {e}")
                    # Continue with trade completion even if evolution fails
            
            await self.bot.db.execute("COMMIT")
            
            self.clear_items()
            await interaction.response.edit_message(content="Trade completed successfully!", view=self)
            
        except Exception as e:
            try:
                await self.bot.db.execute("ROLLBACK")
            except:
                pass
            import logging
            logging.exception(f"Trade failed: {e}")
            await interaction.response.send_message("Trade failed due to a database error. Please try again.", ephemeral=True)
        
    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline_trade(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target_id:
            await interaction.response.send_message("This trade isn't for you!", ephemeral=True)
            return
            
        self.clear_items()
        await interaction.response.edit_message(content="Trade declined.", view=self)

async def setup(bot):
    await bot.add_cog(Trading(bot))