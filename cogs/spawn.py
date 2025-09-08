import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
from io import BytesIO
from data.complete_pokemon_data import COMPLETE_POKEMON_DATA as POKEMON_DATA, RARITY_WEIGHTS

class Spawn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_spawns = {}  # guild_id: {pokemon_data, message}
        
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            return
            
        # Get config
        config = await self.bot.db.fetchrow(
            "SELECT * FROM server_config WHERE guild_id = $1", message.guild.id
        )
        
        # If no config, spawn in all channels
        if not config:
            spawn_channels = [message.channel.id]
        else:
            spawn_channels = config.get('spawn_channels', [])
            # If no spawn channels configured, spawn in all channels
            if not spawn_channels:
                spawn_channels = [message.channel.id]
            
        # XP and money are handled by the Experience cog
        
        # Increment message count
        new_count = config['message_count'] + 1
        await self.bot.db.execute(
            "UPDATE server_config SET message_count = $1 WHERE guild_id = $2",
            new_count, message.guild.id
        )
        
        # Check if spawn should trigger
        if new_count >= config['messages_until_spawn']:
            # Clear old spawns for this guild
            if message.guild.id in self.active_spawns:
                self.active_spawns[message.guild.id].clear()
            
            # Generate single Pokemon data for all channels
            spawn_data = await self._generate_pokemon_data()
            
            # Spawn same Pokemon in all configured spawn channels
            for channel_id in spawn_channels:
                channel = message.guild.get_channel(channel_id)
                if channel:
                    await self._spawn_pokemon(channel, message.guild.id, spawn_data)
            
    async def _generate_pokemon_data(self):
        """Generate Pokemon data for spawning"""
        # Select random Pokemon with evolution bias
        from data.complete_pokemon_data import EVOLUTION_STAGES
        evolution_pool = []
        for pokemon_id, data in POKEMON_DATA.items():
            # Get evolution stage from EVOLUTION_STAGES or default to 1
            evolution_stage = EVOLUTION_STAGES.get(pokemon_id, 1)
            
            # Base forms get higher weight, evolved forms get lower weight but higher levels
            if evolution_stage == 1:  # Base form
                weight = RARITY_WEIGHTS[data['rarity']] * 10
            elif evolution_stage == 2:  # First evolution
                weight = RARITY_WEIGHTS[data['rarity']] * 3
            else:  # Final evolution
                weight = RARITY_WEIGHTS[data['rarity']] * 1
            evolution_pool.extend([pokemon_id] * weight)
            
        species_id = random.choice(evolution_pool)
        pokemon_data = POKEMON_DATA[species_id]
        
        # Level based on evolution stage and rarity
        evolution_stage = EVOLUTION_STAGES.get(species_id, 1)
        if evolution_stage == 1:  # Base form
            level = random.randint(5, 25)
        elif evolution_stage == 2:  # First evolution
            level = random.randint(20, 45)
        else:  # Final evolution
            level = random.randint(35, 62)
            
        # Adjust level based on rarity
        rarity_bonus = {'common': 0, 'uncommon': 5, 'rare': 10, 'legendary': 15}
        level = min(62, level + rarity_bonus[pokemon_data['rarity']])
        
        # Check for shiny (1/4096 chance)
        is_shiny = random.randint(1, 4096) == 1
        
        return {
            'species_id': species_id,
            'level': level,
            'is_shiny': is_shiny
        }
    
    async def _spawn_pokemon(self, channel, guild_id, spawn_data=None):
        # Reset counter and set new spawn requirement (only on first call)
        if spawn_data is None:
            spawn_data = await self._generate_pokemon_data()
            
        new_requirement = random.randint(10, 20)
        await self.bot.db.execute(
            "UPDATE server_config SET message_count = 0, messages_until_spawn = $1 WHERE guild_id = $2",
            new_requirement, guild_id
        )
        
        species_id = spawn_data['species_id']
        level = spawn_data['level']
        is_shiny = spawn_data['is_shiny']
        pokemon_data = POKEMON_DATA[species_id]
        
        # Create spawn embed
        embed = discord.Embed(
            title="A wild Pokemon appeared!",
            description=f"A wild **{pokemon_data['name']}** (Level {level}) appeared!",
            color=0xffd700 if is_shiny else 0x3498db
        )
        
        if is_shiny:
            embed.description += " ✨ **It's shiny!** ✨"
            
        embed.add_field(name="Type", value=f"{pokemon_data['type1']}" + (f"/{pokemon_data['type2']}" if pokemon_data['type2'] else ""), inline=True)
        embed.add_field(name="Rarity", value=pokemon_data['rarity'].title(), inline=True)
        embed.add_field(name="Catch", value="Use `/catch` to attempt capture!", inline=False)
        
        # Try to add Pokemon sprite
        sprite_cog = self.bot.get_cog('SpriteSystem')
        files = []
        if sprite_cog:
            sprite_data = await sprite_cog.get_pokemon_sprite(species_id, is_shiny)
            if sprite_data:
                with BytesIO(sprite_data) as sprite_buffer:
                    # Clean filename by removing special characters
                    clean_name = pokemon_data['name'].lower().replace('♀', '_f').replace('♂', '_m').replace(' ', '_').replace('.', '').replace("'", '')
                    file = discord.File(sprite_buffer, filename=f"{clean_name}.png")
                    embed.set_image(url=f"attachment://{clean_name}.png")
                    files.append(file)
        
        try:
            spawn_message = await channel.send(embed=embed, files=files)
            
            # Store active spawn by guild (shared across all channels)
            if guild_id not in self.active_spawns:
                self.active_spawns[guild_id] = {}
            
            # Use a shared spawn ID for all channels
            spawn_id = f"{species_id}_{level}_{is_shiny}"
            if spawn_id not in self.active_spawns[guild_id]:
                self.active_spawns[guild_id][spawn_id] = {
                    'species_id': species_id,
                    'level': level,
                    'is_shiny': is_shiny,
                    'caught_by': set(),
                    'channels': {}
                }
            
            self.active_spawns[guild_id][spawn_id]['channels'][channel.id] = spawn_message
        except (discord.HTTPException, discord.Forbidden) as e:
            import logging
            logging.error(f"Failed to send spawn message: {e}")
    

        
    @commands.hybrid_command(name="catch", description="Attempt to catch the spawned Pokemon")
    @app_commands.describe(pokeball="Choose a pokeball type")
    @app_commands.choices(pokeball=[
        app_commands.Choice(name="Pokeball", value="pokeball"),
        app_commands.Choice(name="Great Ball", value="greatball"),
        app_commands.Choice(name="Ultra Ball", value="ultraball"),
        app_commands.Choice(name="Master Ball", value="masterball")
    ])
    async def catch(self, ctx, pokeball: str = None):
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        
        # Check if there's an active spawn in this guild
        if guild_id not in self.active_spawns:
            await ctx.send("There's no Pokemon to catch!", ephemeral=True)
            return
            
        # Find spawn in this channel
        spawn_data = None
        spawn_key = None
        for key, data in self.active_spawns[guild_id].items():
            if ctx.channel.id in data.get('channels', {}):
                spawn_data = data
                spawn_key = key
                break
                
        if not spawn_data:
            await ctx.send("There's no Pokemon to catch in this channel!", ephemeral=True)
            return
            
        # Check if user exists
        user = await self.bot.db.get_user(user_id)
        if not user:
            await ctx.send("You haven't started your journey yet! Use `/start` to begin.", ephemeral=True)
            return
            
        # Use default pokeball if none specified
        if not pokeball:
            pokeball = user['default_pokeball']
        else:
            pokeball = pokeball.lower()
            
        # Validate pokeball type
        valid_pokeballs = ["pokeball", "greatball", "ultraball", "masterball"]
        if pokeball not in valid_pokeballs:
            await ctx.send("Invalid pokeball type! Use: pokeball, greatball, ultraball, or masterball", ephemeral=True)
            return
            
        # Check legendary restriction
        if spawn_data['species_id'] not in POKEMON_DATA:
            await ctx.send("Invalid Pokemon data!", ephemeral=True)
            return
        pokemon_data = POKEMON_DATA[spawn_data['species_id']]
        if pokemon_data['rarity'] == 'legendary' and pokeball != 'masterball':
            await ctx.send(f"Legendary Pokemon can only be caught with a Master Ball!", ephemeral=True)
            return
            
        # Check if user has the pokeball
        inventory = await self.bot.db.fetchrow(
            "SELECT quantity FROM user_inventory WHERE user_id = $1 AND item_name = $2",
            user_id, pokeball
        )
        
        if not inventory or inventory['quantity'] <= 0:
            await ctx.send(f"You don't have any {pokeball}s!", ephemeral=True)
            return
            
        # Calculate catch rate
        pokemon_data = POKEMON_DATA[spawn_data['species_id']]
        
        # Base catch rates by rarity (increased)
        rarity_rates = {
            "common": 0.85,
            "uncommon": 0.65, 
            "rare": 0.45,
            "legendary": 0.15
        }
        
        # Pokeball multipliers (increased)
        pokeball_multipliers = {
            "pokeball": 1.2,
            "greatball": 1.8,
            "ultraball": 2.5,
            "masterball": 999.0  # Always catches
        }
        
        base_rate = rarity_rates[pokemon_data['rarity']] * pokeball_multipliers[pokeball]
        base_rate = min(1.0, base_rate)  # Cap at 100%
        
        # Check if user already caught this spawn
        if user_id in spawn_data['caught_by']:
            await ctx.send("You already caught this Pokemon!", ephemeral=True)
            return
        
        # Attempt catch
        if random.random() < base_rate:
            # Success! Add Pokemon to user
            pokemon_id = await self.bot.db.add_pokemon(
                user_id, spawn_data['species_id'], spawn_data['level'], spawn_data['is_shiny']
            )
            
            if pokemon_id is None:
                await ctx.send("You've reached the maximum Pokemon limit (999)! Cannot catch more Pokemon.")
                return
            
            # Initialize moves for the caught Pokemon
            move_learning_cog = self.bot.get_cog('MoveLearning')
            if move_learning_cog:
                await move_learning_cog.initialize_pokemon_moves(pokemon_id, spawn_data['species_id'], spawn_data['level'])
            
            # Remove pokeball from inventory
            await self.bot.db.execute(
                "UPDATE user_inventory SET quantity = quantity - 1 WHERE user_id = $1 AND item_name = $2",
                user_id, pokeball
            )
            
            # Mark as caught by this user
            spawn_data['caught_by'].add(user_id)
            
            shiny_text = "✨ **Shiny** " if spawn_data['is_shiny'] else ""
            embed = discord.Embed(
                title="Gotcha!",
                description=f"You caught the {shiny_text}**{pokemon_data['name']}**!",
                color=0x00ff00
            )
            embed.add_field(name="Level", value=spawn_data['level'], inline=True)
            
            await ctx.send(embed=embed)
            
        else:
            # Failed catch
            await self.bot.db.execute(
                "UPDATE user_inventory SET quantity = quantity - 1 WHERE user_id = $1 AND item_name = $2",
                user_id, pokeball
            )
            
            await ctx.send(f"The {pokemon_data['name']} broke free! Try again with another pokeball.")
            
    @app_commands.command(name="setspawn", description="Set spawn channels (Admin only)")
    @app_commands.describe(
        spawn1="First channel where Pokemon spawn", spawn2="Second spawn channel (optional)", spawn3="Third spawn channel (optional)",
        spawn4="Fourth spawn channel (optional)", spawn5="Fifth spawn channel (optional)", spawn6="Sixth spawn channel (optional)",
        spawn7="Seventh spawn channel (optional)", spawn8="Eighth spawn channel (optional)", spawn9="Ninth spawn channel (optional)", spawn10="Tenth spawn channel (optional)"
    )
    async def setspawn(self, interaction: discord.Interaction, 
                      spawn1: discord.TextChannel,
                      spawn2: discord.TextChannel = None, spawn3: discord.TextChannel = None,
                      spawn4: discord.TextChannel = None, spawn5: discord.TextChannel = None,
                      spawn6: discord.TextChannel = None, spawn7: discord.TextChannel = None,
                      spawn8: discord.TextChannel = None, spawn9: discord.TextChannel = None,
                      spawn10: discord.TextChannel = None):
        if not (interaction.user.guild_permissions.administrator or interaction.user.guild_permissions.manage_guild or interaction.user.guild_permissions.moderate_members or interaction.user.id == 408190648924110858):
            await interaction.response.send_message("This command requires Administrator, Manage Server, or Moderate Members permissions!", ephemeral=True)
            return
            
        spawn_channels = [spawn1]
        
        for spawn in [spawn2, spawn3, spawn4, spawn5, spawn6, spawn7, spawn8, spawn9, spawn10]:
            if spawn:
                spawn_channels.append(spawn)
            
        spawn_ids = [channel.id for channel in spawn_channels]
        
        try:
            await self.bot.db.execute(
                """INSERT INTO server_config (guild_id, spawn_channels, message_count, messages_until_spawn)
                   VALUES ($1, $2, 0, $3)
                   ON CONFLICT (guild_id) DO UPDATE SET spawn_channels = $2""",
                interaction.guild.id, spawn_ids, random.randint(10, 20)
            )
        except Exception as e:
            await interaction.response.send_message("Database error occurred while updating spawn configuration!", ephemeral=True)
            return
        
        spawn_mentions = ", ".join([channel.mention for channel in spawn_channels])
        await interaction.response.send_message(f"Pokemon will spawn in: {spawn_mentions}\nMonitoring all server channels for messages.")

async def setup(bot):
    await bot.add_cog(Spawn(bot))