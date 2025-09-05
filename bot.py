import discord
from discord.ext import commands
import asyncpg
import os
from dotenv import load_dotenv
import asyncio
import logging
# Pokemon data is imported by individual cogs as needed
from utils.database import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pokebot.log'),
        logging.StreamHandler()
    ]
)

load_dotenv()

class PokemonBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.db = None
        
    async def setup_hook(self):
        self.db = Database(os.getenv('DATABASE_URL'))
        await self.db.connect()
        await self.load_extension('cogs.core')
        await self.load_extension('cogs.pokemon')
        await self.load_extension('cogs.spawn')
        await self.load_extension('cogs.battle')
        await self.load_extension('cogs.experience')
        await self.load_extension('cogs.shop')
        await self.load_extension('cogs.admin')
        await self.load_extension('cogs.gym')
        await self.load_extension('cogs.trading')
        await self.load_extension('cogs.evolution')
        await self.load_extension('cogs.moves')
        await self.load_extension('cogs.config')
        await self.load_extension('cogs.status_effects')
        await self.load_extension('cogs.rate_limiter')
        await self.load_extension('cogs.battle_accept')
        await self.load_extension('cogs.caching')
        await self.load_extension('cogs.sprites')
        await self.load_extension('cogs.backup_system')
        await self.load_extension('cogs.help_system')
        await self.load_extension('cogs.statistics')
        await self.load_extension('cogs.error_handler')
        await self.load_extension('cogs.pokedex')
        await self.load_extension('cogs.invite')
        await self.load_extension('cogs.move_learning')
        await self.load_extension('cogs.move_validator_v2')

        
    async def on_ready(self):
        import logging
        logging.info(f'{self.user} has connected to Discord!')
        await self.tree.sync()
        logging.info('Slash commands synced!')
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.guild is None:
            await interaction.response.send_message("This bot can only be used in servers, not in DMs!", ephemeral=True)
            return False
        return True

bot = PokemonBot()

if __name__ == '__main__':
    token = os.getenv('DISCORD_TOKEN')
    import logging
    if not token:
        logging.error("DISCORD_TOKEN not found in environment variables. Please check your .env file.")
        exit(1)
        
    try:
        bot.run(token)
    except discord.LoginFailure:
        logging.error("Invalid Discord token. Please check your .env file.")
        exit(1)
    except discord.HTTPException as e:
        logging.error(f"Discord HTTP error: {e}")
        exit(1)
    except Exception as e:
        logging.error(f"Failed to start bot: {e}")
        exit(1)