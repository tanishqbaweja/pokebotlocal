import discord
from discord.ext import commands, tasks
import time
from collections import defaultdict, deque

class RateLimiter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_cooldowns = defaultdict(lambda: deque())
        self.cleanup_task.start()
        self.command_limits = {
            'catch': (5, 60),    # 5 uses per 60 seconds
            'battle': (3, 300),  # 3 uses per 5 minutes
            'trade': (5, 300),   # 5 uses per 5 minutes
            'shop': (10, 60),    # 10 uses per minute
            'buy': (10, 60)      # 10 purchases per minute
        }
        
    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction, command):
        """Track command usage for rate limiting"""
        if not command or interaction.user.bot:
            return
            
        command_name = command.name
        if command_name not in self.command_limits:
            return
            
        user_id = interaction.user.id
        current_time = time.time()
        max_uses, window = self.command_limits[command_name]
        
        # Clean old entries
        user_queue = self.user_cooldowns[f"{user_id}_{command_name}"]
        while user_queue and current_time - user_queue[0] > window:
            user_queue.popleft()
            
        # Add current usage
        user_queue.append(current_time)
        
    def is_rate_limited(self, user_id, command_name):
        """Check if user is rate limited for a command"""
        if command_name not in self.command_limits:
            return False
            
        current_time = time.time()
        max_uses, window = self.command_limits[command_name]
        user_queue = self.user_cooldowns[f"{user_id}_{command_name}"]
        
        # Clean old entries
        while user_queue and current_time - user_queue[0] > window:
            user_queue.popleft()
            
        return len(user_queue) >= max_uses
        
    def get_cooldown_time(self, user_id, command_name):
        """Get remaining cooldown time in seconds"""
        if command_name not in self.command_limits:
            return 0
            
        current_time = time.time()
        window = self.command_limits[command_name][1]
        user_queue = self.user_cooldowns[f"{user_id}_{command_name}"]
        
        if not user_queue:
            return 0
            
        oldest_use = user_queue[0]
        return max(0, window - (current_time - oldest_use))
        
    @tasks.loop(hours=1)
    async def cleanup_task(self):
        """Clean up old cooldown entries to prevent memory leaks"""
        current_time = time.time()
        keys_to_remove = []
        
        for key, queue in self.user_cooldowns.items():
            # Clean old entries from each queue
            while queue and current_time - queue[0] > 3600:  # Remove entries older than 1 hour
                queue.popleft()
            
            # Remove empty queues
            if not queue:
                keys_to_remove.append(key)
                
        for key in keys_to_remove:
            del self.user_cooldowns[key]
            
    def cog_unload(self):
        self.cleanup_task.cancel()

async def setup(bot):
    await bot.add_cog(RateLimiter(bot))