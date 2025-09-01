import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime, timedelta

class Trading(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="trade", description="Offer a trade to another user")
    async def trade(self, interaction: discord.Interaction, user: discord.Member, position: int):
        requester_id = interaction.user.id
        target_id = user.id

        # Rate Limiter Check
        rate_limiter = self.bot.get_cog('RateLimiter')
        if rate_limiter and rate_limiter.is_rate_limited(requester_id, 'trade'):
            cooldown = rate_limiter.get_cooldown_time(requester_id, 'trade')
            await interaction.response.send_message(f"You're trading too frequently! Try again in {cooldown:.1f} seconds.", ephemeral=True)
            return
        
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
            
        if position < 1 or position > 6:
            await interaction.response.send_message("Position must be between 1 and 6!", ephemeral=True)
            return
            
        # Get requester's Pokemon from party position
        requester_pokemon = await self.bot.db.fetchrow(
            "SELECT * FROM pokemon WHERE owner_id = $1 AND in_party = TRUE AND party_position = $2",
            requester_id, position
        )
        
        if not requester_pokemon:
            await interaction.response.send_message(f"No Pokemon at position {position} in your party!", ephemeral=True)
            return
            
        # Check for existing active trades for either user
        # This is a simplified lock, a better implementation would be a 'status' on the pokemon table
        existing_trade = await self.bot.db.fetchrow(
            "SELECT id FROM trades WHERE (requester_id = $1 OR target_id = $1 OR requester_id = $2 OR target_id = $2) AND status = 'pending'",
            requester_id, target_id
        )
        
        if existing_trade:
            await interaction.response.send_message("One of you already has an active trade request!", ephemeral=True)
            return
            
        from data.complete_pokemon_data import COMPLETE_POKEMON_DATA
        requester_species = COMPLETE_POKEMON_DATA[requester_pokemon['species_id']]
        
        # Create the initial trade offer view
        embed = discord.Embed(
            title="Trade Offer",
            description=f"{interaction.user.mention} is offering their **{requester_species['name']}** (Lv.{requester_pokemon['level']}).\n\n"
                        f"{user.mention}, please select a Pokémon from your party to offer in return.",
            color=0x3498db
        )
        
        target_party = await self.bot.db.fetch("SELECT * FROM pokemon WHERE owner_id = $1 AND in_party = TRUE ORDER BY party_position", target_id)

        view = TradeOfferView(self.bot, requester_id, target_id, requester_pokemon, target_party)
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
        
    async def execute_trade(self, interaction: discord.Interaction, pokemon1_id, pokemon2_id):
        """Executes the final trade within a database transaction."""
        
        pokemon1 = await self.bot.db.fetchrow("SELECT * FROM pokemon WHERE id = $1", pokemon1_id)
        pokemon2 = await self.bot.db.fetchrow("SELECT * FROM pokemon WHERE id = $1", pokemon2_id)

        if not pokemon1 or not pokemon2:
            raise Exception("One of the Pokémon could not be found.")

        owner1_id = pokemon1['owner_id']
        owner2_id = pokemon2['owner_id']

        # Basic check to prevent trading last pokemon
        party_count1 = await self._get_party_count(owner1_id)
        party_count2 = await self._get_party_count(owner2_id)
        if (pokemon1['in_party'] and party_count1 <= 1) or \
           (pokemon2['in_party'] and party_count2 <= 1):
            raise Exception("A trainer cannot trade their last party Pokémon.")

        await self.bot.db.execute("BEGIN")
        try:
            # Swap ownership and move to PC
            await self.bot.db.execute(
                "UPDATE pokemon SET owner_id = $1, in_party = FALSE, party_position = NULL WHERE id = $2",
                owner2_id, pokemon1_id
            )
            await self.bot.db.execute(
                "UPDATE pokemon SET owner_id = $1, in_party = FALSE, party_position = NULL WHERE id = $2",
                owner1_id, pokemon2_id
            )
            
            await self.bot.db.execute("COMMIT")

            # Handle trade evolutions after the transaction is committed
            await self._check_trade_evolution(interaction, pokemon1_id)
            await self._check_trade_evolution(interaction, pokemon2_id)
            
        except Exception as e:
            await self.bot.db.execute("ROLLBACK")
            raise e
            
    # Trade evolution mapping as class constant
    TRADE_EVOLUTIONS = {
        64: 65,   # Kadabra -> Alakazam
        67: 68,   # Machoke -> Machamp
        93: 94,   # Haunter -> Gengar
        75: 76    # Graveler -> Golem
    }
    
    async def _check_trade_evolution(self, interaction: discord.Interaction, pokemon_id):
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
            old_species_data = COMPLETE_POKEMON_DATA[species_id]
            new_species_data = COMPLETE_POKEMON_DATA[new_species]

            old_max_hp = ((old_species_data['base_hp'] + pokemon['hp_iv']) * 2 * pokemon['level'] // 100) + pokemon['level'] + 10
            new_max_hp = ((new_species_data['base_hp'] + pokemon['hp_iv']) * 2 * pokemon['level'] // 100) + pokemon['level'] + 10
            
            hp_increase = new_max_hp - old_max_hp
            new_current_hp = pokemon['current_hp'] + hp_increase

            await self.bot.db.execute(
                "UPDATE pokemon SET current_hp = $1 WHERE id = $2",
                new_current_hp, pokemon_id
            )
            
            # Log evolution and send notification to channel
            old_name = COMPLETE_POKEMON_DATA[species_id]['name']
            new_name = new_species_data['name']
            import logging
            logging.info(f"Trade evolution: {old_name} -> {new_name} (Pokemon ID: {pokemon_id})")
            
            embed = discord.Embed(
                title="Trade Evolution!",
                description=f"<@{pokemon['owner_id']}>'s {old_name} evolved into {new_name} through trading!",
                color=0xffd700
            )
            await interaction.channel.send(embed=embed)
            
    async def _get_party_count(self, user_id):
        return await self.bot.db.fetchval(
            "SELECT COUNT(*) FROM pokemon WHERE owner_id = $1 AND in_party = TRUE",
            user_id
        )

class TradeOfferView(discord.ui.View):
    def __init__(self, bot, requester_id, target_id, requester_pokemon, target_party):
        super().__init__(timeout=300)
        self.bot = bot
        self.requester_id = requester_id
        self.target_id = target_id
        self.requester_pokemon = requester_pokemon
        self.message = None

        from data.complete_pokemon_data import COMPLETE_POKEMON_DATA

        options = []
        for pokemon in target_party:
            species = COMPLETE_POKEMON_DATA[pokemon['species_id']]
            options.append(discord.SelectOption(label=f"Lv.{pokemon['level']} {species['name']}", value=str(pokemon['id'])))

        pokemon_select = discord.ui.Select(placeholder="Choose a Pokémon to offer...", options=options)
        pokemon_select.callback = self.select_pokemon
        self.add_item(pokemon_select)

        decline_button = discord.ui.Button(label="Decline", style=discord.ButtonStyle.red)
        decline_button.callback = self.decline_trade
        self.add_item(decline_button)

    async def select_pokemon(self, interaction: discord.Interaction):
        if interaction.user.id != self.target_id:
            await interaction.response.send_message("This trade isn't for you!", ephemeral=True)
            return

        target_pokemon_id = int(interaction.data['values'][0])
        target_pokemon = await self.bot.db.fetchrow("SELECT * FROM pokemon WHERE id = $1", target_pokemon_id)

        # Transition to confirmation view
        from data.complete_pokemon_data import COMPLETE_POKEMON_DATA
        requester_species = COMPLETE_POKEMON_DATA[self.requester_pokemon['species_id']]
        target_species = COMPLETE_POKEMON_DATA[target_pokemon['species_id']]
        
        embed = discord.Embed(
            title="Trade Confirmation",
            description=f"Please confirm the trade:\n\n"
                        f"<@{self.requester_id}> offers: **{requester_species['name']}** (Lv.{self.requester_pokemon['level']})\n"
                        f"<@{self.target_id}> offers: **{target_species['name']}** (Lv.{target_pokemon['level']})\n\n"
                        f"Both trainers must click 'Confirm' to complete the trade.",
            color=0xf1c40f
        )
        
        view = TradeConfirmationView(self.bot, self.requester_id, self.target_id, self.requester_pokemon, target_pokemon)
        await interaction.response.edit_message(embed=embed, view=view)
        view.message = await interaction.original_response()

    async def decline_trade(self, interaction: discord.Interaction):
        if interaction.user.id != self.target_id and interaction.user.id != self.requester_id:
            await interaction.response.send_message("This trade isn't for you!", ephemeral=True)
            return
            
        self.clear_items()
        await self.message.edit(content="Trade declined by user.", view=self)

    async def on_timeout(self):
        self.clear_items()
        await self.message.edit(content="Trade offer expired.", view=self)

class TradeConfirmationView(discord.ui.View):
    def __init__(self, bot, requester_id, target_id, requester_pokemon, target_pokemon):
        super().__init__(timeout=120)
        self.bot = bot
        self.requester_id = requester_id
        self.target_id = target_id
        self.requester_pokemon = requester_pokemon
        self.target_pokemon = target_pokemon
        self.requester_confirmed = False
        self.target_confirmed = False
        self.message = None

    @discord.ui.button(label="Confirm Trade", style=discord.ButtonStyle.green)
    async def confirm_trade(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        if user_id not in [self.requester_id, self.target_id]:
            await interaction.response.send_message("This trade isn't for you!", ephemeral=True)
            return

        if user_id == self.requester_id:
            self.requester_confirmed = True
        elif user_id == self.target_id:
            self.target_confirmed = True
            
        await interaction.response.send_message(f"<@{user_id}> has confirmed the trade.", ephemeral=True)
            
        if self.requester_confirmed and self.target_confirmed:
            self.clear_items()
            await self.message.edit(content="Trade confirmed by both parties! Processing...", view=self)
            
            # Execute the trade
            trading_cog = self.bot.get_cog('Trading')
            try:
                await trading_cog.execute_trade(interaction, self.requester_pokemon['id'], self.target_pokemon['id'])
                await self.message.edit(content="Trade completed successfully!")
            except Exception as e:
                import logging
                logging.exception(f"Trade execution failed: {e}")
                await self.message.edit(content=f"An error occurred during the trade: {e}")

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel_trade(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        if user_id not in [self.requester_id, self.target_id]:
            await interaction.response.send_message("This trade isn't for you!", ephemeral=True)
            return
            
        self.clear_items()
        await self.message.edit(content=f"Trade cancelled by <@{user_id}>.", view=self)

    async def on_timeout(self):
        self.clear_items()
        await self.message.edit(content="Trade confirmation expired.", view=self)

async def setup(bot):
    await bot.add_cog(Trading(bot))