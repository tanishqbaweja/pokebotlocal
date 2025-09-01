import discord
from discord.ext import commands
from PIL import Image
import aiohttp
import asyncio
from io import BytesIO

class SpriteSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sprite_cache = {}
        self.sprite_base_url = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/"
        self.session = None
        
    async def get_pokemon_sprite(self, species_id, is_shiny=False):
        """Get Pokemon sprite image"""
        cache_key = f"{species_id}_{'shiny' if is_shiny else 'normal'}"
        
        if cache_key in self.sprite_cache:
            return self.sprite_cache[cache_key]
            
        try:
            if is_shiny:
                url = f"{self.sprite_base_url}shiny/{species_id}.png"
            else:
                url = f"{self.sprite_base_url}{species_id}.png"
                
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.get(url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    self.sprite_cache[cache_key] = image_data
                    return image_data
                        
        except Exception as e:
            print(f"Error loading sprite for Pokemon {species_id}: {e}")
            
        return None
        
    def cog_unload(self):
        if self.session:
            asyncio.create_task(self.session.close())

async def setup(bot):
    await bot.add_cog(SpriteSystem(bot))