import discord
from discord.ext import commands, tasks
import asyncio
import os
import subprocess
from datetime import datetime

class BackupSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backup_directory = "backups"
        self.database_url = os.getenv('DATABASE_URL')
        
    @commands.Cog.listener()
    async def on_ready(self):
        """Start backup task when bot is ready"""
        if not os.path.exists(self.backup_directory):
            os.makedirs(self.backup_directory)
        self.backup_task.start()
        
    @tasks.loop(hours=6)  # Every 6 hours
    async def backup_task(self):
        """Perform automatic database backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{self.backup_directory}/pokebot_backup_{timestamp}.sql"
            
            # Extract database connection details
            if self.database_url:
                # Use pg_dump to create backup
                cmd = f"pg_dump {self.database_url} > {backup_file}"
                
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    print(f"Database backup created: {backup_file}")
                    
                    # Keep only last 10 backups
                    await self._cleanup_old_backups()
                else:
                    print(f"Backup failed: {stderr.decode()}")
                    
        except Exception as e:
            print(f"Backup error: {e}")
            
    async def _cleanup_old_backups(self):
        """Remove old backup files, keep only the 10 most recent"""
        try:
            backup_files = [
                f for f in os.listdir(self.backup_directory) 
                if f.startswith("pokebot_backup_") and f.endswith(".sql")
            ]
            
            backup_files.sort(reverse=True)  # Most recent first
            
            # Remove files beyond the 10 most recent
            for old_backup in backup_files[10:]:
                old_path = os.path.join(self.backup_directory, old_backup)
                os.remove(old_path)
                print(f"Removed old backup: {old_backup}")
                
        except Exception as e:
            print(f"Cleanup error: {e}")
            
    @commands.command(name="backup", hidden=True)
    @commands.is_owner()
    async def manual_backup(self, ctx):
        """Manually trigger a database backup"""
        await ctx.send("Starting manual backup...")
        await self.backup_task()
        await ctx.send("Manual backup completed!")

async def setup(bot):
    await bot.add_cog(BackupSystem(bot))