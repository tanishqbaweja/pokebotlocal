import discord
from discord.ext import commands
from discord import app_commands
import random
from io import BytesIO
from data.complete_pokemon_data import COMPLETE_POKEMON_DATA as POKEMON_DATA

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admin_id = 408190648924110858
        
    def is_admin(self, user_id):
        return user_id == self.admin_id
        
    @app_commands.command(name="spawn", description="Force spawn a Pokemon (Admin only)")
    async def force_spawn(self, interaction: discord.Interaction, pokemon: str, level: int = None, shiny: bool = False):
        if not self.is_admin(interaction.user.id):
            await interaction.response.send_message("Admin only command!", ephemeral=True)
            return
            
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in servers!", ephemeral=True)
            return
            
        # Find Pokemon by name
        species_id = None
        for pid, data in POKEMON_DATA.items():
            if data['name'].lower() == pokemon.lower():
                species_id = pid
                break
                
        if not species_id:
            await interaction.response.send_message("Pokemon not found!", ephemeral=True)
            return
            
        # Get spawn channels for this server
        config = await self.bot.db.fetchrow(
            "SELECT * FROM server_config WHERE guild_id = $1", interaction.guild.id
        )
        
        if not config or not config['spawn_channels']:
            await interaction.response.send_message("No spawn channels configured! Use /setspawn first.", ephemeral=True)
            return
            
        # Parse spawn channels
        all_channels = config.get('spawn_channels', [])
        if -1 in all_channels:
            separator_index = all_channels.index(-1)
            spawn_channels = all_channels[separator_index + 1:]
        else:
            spawn_channels = all_channels
            
        # Use the same spawn system
        spawn_cog = self.bot.get_cog('Spawn')
        if spawn_cog:
            # Calculate level using same logic as normal spawns if not specified
            if level is None:
                pokemon_data = POKEMON_DATA[species_id]
                evolution_stage = pokemon_data.get('evolution_stage', 1)
                if evolution_stage == 1:  # Base form
                    level = random.randint(5, 25)
                elif evolution_stage == 2:  # First evolution
                    level = random.randint(20, 45)
                else:  # Final evolution
                    level = random.randint(35, 62)
                    
                # Adjust level based on rarity
                rarity_bonus = {'common': 0, 'uncommon': 5, 'rare': 10, 'legendary': 15}
                level = min(62, level + rarity_bonus[pokemon_data['rarity']])
            
            # Create spawn data
            spawn_data = {
                'species_id': species_id,
                'level': level,
                'is_shiny': shiny
            }
            
            # Spawn in all configured spawn channels
            spawned_count = 0
            for channel_id in spawn_channels:
                channel = interaction.guild.get_channel(channel_id)
                if channel:
                    await spawn_cog._spawn_pokemon(channel, interaction.guild.id, spawn_data)
                    spawned_count += 1
            
            await interaction.response.send_message(f"Pokemon spawned in {spawned_count} channels!", ephemeral=True)
        
    @app_commands.command(name="givemoney", description="Give money to a user (Admin only)")
    async def give_money(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        if not self.is_admin(interaction.user.id):
            await interaction.response.send_message("Admin only command!", ephemeral=True)
            return
            
        try:
            await self.bot.db.execute(
                "UPDATE users SET money = money + $1 WHERE user_id = $2",
                amount, user.id
            )
        except Exception as e:
            import logging
            logging.error(f"Admin give money error: {e}")
            await interaction.response.send_message(f"Database error: {e}", ephemeral=True)
            return
        
        await interaction.response.send_message(f"Gave {amount:,} rupees to {user.mention}")
        
    @app_commands.command(name="giveitem", description="Give items to a user (Admin only)")
    async def give_item(self, interaction: discord.Interaction, user: discord.Member, item: str, quantity: int):
        if not self.is_admin(interaction.user.id):
            await interaction.response.send_message("Admin only command!", ephemeral=True)
            return
            
        item = item.lower().replace(' ', '_')
        
        try:
            await self.bot.db.execute(
                """INSERT INTO user_inventory (user_id, item_name, quantity)
                   VALUES ($1, $2, $3)
                   ON CONFLICT (user_id, item_name)
                   DO UPDATE SET quantity = user_inventory.quantity + $3""",
                user.id, item, quantity
            )
        except Exception as e:
            import logging
            logging.error(f"Admin give item error: {e}")
            await interaction.response.send_message(f"Database error: {e}", ephemeral=True)
            return
        
        await interaction.response.send_message(f"Gave {quantity}x {item.replace('_', ' ').title()} to {user.mention}")
        
    @app_commands.command(name="resetuser", description="Reset a user's progress (Admin only)")
    async def reset_user(self, interaction: discord.Interaction, user: discord.Member):
        if not self.is_admin(interaction.user.id):
            await interaction.response.send_message("Admin only command!", ephemeral=True)
            return
            
        # Delete user's data in correct order to avoid foreign key violations
        try:
            await self.bot.db.execute("DELETE FROM battles WHERE challenger_id = $1 OR opponent_id = $1", user.id)
            await self.bot.db.execute("DELETE FROM pokemon WHERE owner_id = $1", user.id)
            await self.bot.db.execute("DELETE FROM user_inventory WHERE user_id = $1", user.id)
            await self.bot.db.execute("DELETE FROM users WHERE user_id = $1", user.id)
        except Exception as e:
            import logging
            logging.error(f"Admin reset user error: {e}")
            await interaction.response.send_message(f"Database error: {e}", ephemeral=True)
            return
        
        await interaction.response.send_message(f"Reset {user.mention}'s progress")
        
    @app_commands.command(name="setlevel", description="Set a Pokemon's level (Admin only)")
    async def set_level(self, interaction: discord.Interaction, user: discord.Member, pokemon_id: int, level: int):
        if not self.is_admin(interaction.user.id):
            await interaction.response.send_message("Admin only command!", ephemeral=True)
            return
            
        if level < 1 or level > 100:
            await interaction.response.send_message("Level must be between 1 and 100!", ephemeral=True)
            return
            
        try:
            # Update Pokemon level and recalculate HP
            pokemon = await self.bot.db.fetchrow(
                "SELECT * FROM pokemon WHERE id = $1 AND owner_id = $2",
                pokemon_id, user.id
            )
            
            if not pokemon:
                await interaction.response.send_message("Pokemon not found!", ephemeral=True)
                return
                
            from data.complete_pokemon_data import COMPLETE_POKEMON_DATA
            species = COMPLETE_POKEMON_DATA[pokemon['species_id']]
            new_hp = ((species['base_hp'] + pokemon['hp_iv']) * 2 * level // 100) + level + 10
            
            await self.bot.db.execute(
                "UPDATE pokemon SET level = $1, current_hp = $2 WHERE id = $3",
                level, new_hp, pokemon_id
            )
        except Exception as e:
            import logging
            logging.error(f"Admin setlevel error: {e}")
            await interaction.response.send_message(f"Database error: {e}", ephemeral=True)
            return
        
        await interaction.response.send_message(f"Set Pokemon #{pokemon_id} to level {level}")

async def setup(bot):
    await bot.add_cog(Admin(bot))