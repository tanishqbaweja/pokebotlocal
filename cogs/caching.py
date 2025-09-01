import discord
from discord.ext import commands
import asyncio
from collections import defaultdict
import time

class CachingSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pokemon_cache = {}  # species_id: pokemon_data
        self.move_cache = {}     # move_name: move_data
        self.user_cache = {}     # user_id: user_data
        self.cache_timestamps = defaultdict(float)
        self.cache_ttl = 300     # 5 minutes TTL
        
    async def get_pokemon_data(self, species_id):
        """Get cached Pokemon species data"""
        cache_key = f"pokemon_{species_id}"
        
        if self._is_cache_valid(cache_key):
            return self.pokemon_cache.get(species_id)
            
        # Load from data file
        from data.complete_pokemon_data import COMPLETE_POKEMON_DATA
        if species_id in COMPLETE_POKEMON_DATA:
            self.pokemon_cache[species_id] = COMPLETE_POKEMON_DATA[species_id]
            self.cache_timestamps[cache_key] = time.time()
            return self.pokemon_cache[species_id]
            
        return None
        
    async def get_move_data(self, move_name):
        """Get cached move data"""
        cache_key = f"move_{move_name}"
        
        if self._is_cache_valid(cache_key):
            return self.move_cache.get(move_name)
            
        # Load from data file
        from data.complete_moves_data import COMPLETE_MOVES_DATA
        if move_name in COMPLETE_MOVES_DATA:
            self.move_cache[move_name] = COMPLETE_MOVES_DATA[move_name]
            self.cache_timestamps[cache_key] = time.time()
            return self.move_cache[move_name]
            
        return None
        
    async def get_user_data(self, user_id):
        """Get cached user data"""
        cache_key = f"user_{user_id}"
        
        if self._is_cache_valid(cache_key):
            return self.user_cache.get(user_id)
            
        # Load from database
        user_data = await self.bot.db.get_user(user_id)
        if user_data:
            self.user_cache[user_id] = dict(user_data)
            self.cache_timestamps[cache_key] = time.time()
            return self.user_cache[user_id]
            
        return None
        
    def invalidate_user_cache(self, user_id):
        """Invalidate user cache when data changes"""
        cache_key = f"user_{user_id}"
        if user_id in self.user_cache:
            del self.user_cache[user_id]
        if cache_key in self.cache_timestamps:
            del self.cache_timestamps[cache_key]
            
    def _is_cache_valid(self, cache_key):
        """Check if cache entry is still valid"""
        if cache_key not in self.cache_timestamps:
            return False
        return time.time() - self.cache_timestamps[cache_key] < self.cache_ttl
        
    @commands.Cog.listener()
    async def on_ready(self):
        """Start cache cleanup task"""
        self.cleanup_task = asyncio.create_task(self._cleanup_cache())
        
    async def _cleanup_cache(self):
        """Periodically clean expired cache entries"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                current_time = time.time()
                
                expired_keys = [
                    key for key, timestamp in self.cache_timestamps.items()
                    if current_time - timestamp > self.cache_ttl
                ]
                
                for key in expired_keys:
                    del self.cache_timestamps[key]
                    
                    if key.startswith('pokemon_'):
                        species_id = int(key.split('_')[1])
                        self.pokemon_cache.pop(species_id, None)
                    elif key.startswith('move_'):
                        move_name = key.split('_', 1)[1]
                        self.move_cache.pop(move_name, None)
                    elif key.startswith('user_'):
                        user_id = int(key.split('_')[1])
                        self.user_cache.pop(user_id, None)
            except Exception as e:
                import logging
                logging.exception(f"Cache cleanup error: {e}")
                
    def cog_unload(self):
        """Cancel cleanup task when cog is unloaded"""
        if hasattr(self, 'cleanup_task'):
            self.cleanup_task.cancel()

async def setup(bot):
    await bot.add_cog(CachingSystem(bot))