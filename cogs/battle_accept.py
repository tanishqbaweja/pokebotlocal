import discord
from discord.ext import commands

class BattleAccept(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pending_battles = {}  # challenger_id: {opponent_id, challenger_pokemon, opponent_pokemon, channel, timestamp}
        self.cleanup_task = None
        
    @commands.hybrid_command(name="accept", description="Accept a battle challenge")
    async def accept_battle(self, ctx, challenger: discord.Member):
        opponent_id = ctx.author.id
        challenger_id = challenger.id
        
        # Check if there's a pending battle from this challenger
        if challenger_id not in self.pending_battles:
            await ctx.send("No pending battle request from this user!", ephemeral=True)
            return
            
        battle_data = self.pending_battles[challenger_id]
        
        # Verify the opponent matches
        if battle_data['opponent_id'] != opponent_id:
            await ctx.send("This battle request isn't for you!", ephemeral=True)
            return
            
        # Start the battle
        battle_cog = self.bot.get_cog('Battle')
        if battle_cog:
            await battle_cog.start_battle(
                ctx.channel,
                challenger_id,
                opponent_id,
                battle_data['challenger_pokemon'],
                battle_data['opponent_pokemon']
            )
            
            # Remove from pending battles
            del self.pending_battles[challenger_id]
            
            await ctx.send("Battle accepted! Let the battle begin!")
        else:
            await ctx.send("Battle system not available!", ephemeral=True)
            
    def add_pending_battle(self, challenger_id, opponent_id, challenger_pokemon, opponent_pokemon, channel):
        """Add a pending battle request"""
        import time
        self.pending_battles[challenger_id] = {
            'opponent_id': opponent_id,
            'challenger_pokemon': challenger_pokemon,
            'opponent_pokemon': opponent_pokemon,
            'channel': channel,
            'timestamp': time.time()
        }
        
        # Start cleanup task if not running
        if not self.cleanup_task:
            import asyncio
            self.cleanup_task = asyncio.create_task(self._cleanup_expired_battles())
            
    async def _cleanup_expired_battles(self):
        """Clean up expired battle requests (older than 5 minutes)"""
        import asyncio
        import time
        
        while True:
            await asyncio.sleep(60)  # Check every minute
            current_time = time.time()
            expired_battles = []
            
            for challenger_id, battle_data in self.pending_battles.items():
                if current_time - battle_data['timestamp'] > 300:  # 5 minutes
                    expired_battles.append(challenger_id)
                    
            for challenger_id in expired_battles:
                del self.pending_battles[challenger_id]
                
    def cog_unload(self):
        if self.cleanup_task:
            self.cleanup_task.cancel()

async def setup(bot):
    await bot.add_cog(BattleAccept(bot))