"""
Enhanced Move Validator v2 - Ensures all moves are properly implemented
"""

import discord
from discord.ext import commands
from discord import app_commands
import os
from data.complete_moves_data import COMPLETE_MOVES_DATA as MOVES_DATA

class MoveValidatorV2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Moves that should be implemented in battle system
        self.required_move_implementations = {
            # Status moves that need special handling
            'status_moves': [
                'growl', 'tail_whip', 'leer', 'screech', 'acid', 'sand_attack', 'smokescreen', 'flash', 'kinesis',
                'swords_dance', 'sharpen', 'meditate', 'harden', 'withdraw', 'defense_curl', 'acid_armor',
                'agility', 'string_shot', 'amnesia', 'barrier', 'growth', 'poison_powder', 'poison_gas', 'toxic',
                'sleep_powder', 'spore', 'sing', 'hypnosis', 'lovely_kiss', 'stun_spore', 'thunder_wave', 'glare',
                'supersonic', 'confuse_ray', 'recover', 'rest', 'soft_boiled', 'transform', 'double_team', 'minimize',
                'haze', 'mist', 'light_screen', 'reflect', 'leech_seed', 'substitute', 'teleport', 'whirlwind', 'roar',
                'splash', 'disable', 'focus_energy', 'conversion', 'mimic'
            ],
            
            # Fixed damage moves
            'fixed_damage_moves': [
                'sonic_boom', 'dragon_rage', 'night_shade', 'seismic_toss', 'super_fang', 'psywave'
            ],
            
            # Self-fainting moves
            'self_faint_moves': [
                'selfdestruct', 'explosion'
            ],
            
            # OHKO moves
            'ohko_moves': [
                'fissure', 'guillotine', 'horn_drill'
            ],
            
            # Multi-hit moves
            'multi_hit_moves': [
                'double_slap', 'comet_punch', 'fury_attack', 'pin_missile', 'spike_cannon', 'barrage', 'fury_swipes'
            ],
            
            # Recoil moves
            'recoil_moves': [
                'take_down', 'double_edge', 'submission', 'jump_kick', 'high_jump_kick'
            ],
            
            # Two-turn moves
            'two_turn_moves': [
                'skull_bash', 'sky_attack', 'razor_wind', 'solar_beam', 'dig', 'fly'
            ]
        }
        
    @app_commands.command(name="validatemoves", description="Validate all move implementations (Admin only)")
    async def validate_moves(self, interaction: discord.Interaction):
        # Check admin permissions
        admin_user_id = int(os.getenv('ADMIN_USER_ID', 0)) if os.getenv('ADMIN_USER_ID') else 0
        if interaction.user.id != admin_user_id:
            await interaction.response.send_message("This command is for administrators only!", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        # Check battle system implementation
        battle_cog = self.bot.get_cog('Battle')
        if not battle_cog:
            await interaction.followup.send("Battle system not loaded!")
            return
            
        missing_implementations = []
        working_moves = []
        
        # Test each move category
        for category, moves in self.required_move_implementations.items():
            for move_name in moves:
                if move_name in MOVES_DATA:
                    # Check if move is handled in battle system
                    is_implemented = self._check_move_implementation(battle_cog, move_name, category)
                    if is_implemented:
                        working_moves.append(f"{move_name} ({category})")
                    else:
                        missing_implementations.append(f"{move_name} ({category})")
                        
        # Create report
        embed = discord.Embed(title="Move Implementation Report", color=0x00ff00 if not missing_implementations else 0xff0000)
        
        if working_moves:
            # Split into chunks to avoid field limit
            working_chunks = [working_moves[i:i+20] for i in range(0, len(working_moves), 20)]
            for i, chunk in enumerate(working_chunks):
                embed.add_field(
                    name=f"Working Moves ({len(working_moves)} total) - Part {i+1}",
                    value="\n".join(chunk[:10]) + ("\n..." if len(chunk) > 10 else ""),
                    inline=False
                )
                
        if missing_implementations:
            missing_chunks = [missing_implementations[i:i+20] for i in range(0, len(missing_implementations), 20)]
            for i, chunk in enumerate(missing_chunks):
                embed.add_field(
                    name=f"Missing Implementations ({len(missing_implementations)} total) - Part {i+1}",
                    value="\n".join(chunk[:10]) + ("\n..." if len(chunk) > 10 else ""),
                    inline=False
                )
        else:
            embed.add_field(name="Status", value="✅ All required moves are implemented!", inline=False)
            
        await interaction.followup.send(embed=embed)
        
    def _check_move_implementation(self, battle_cog, move_name, category):
        """Check if a move is properly implemented in the battle system"""
        try:
            # Get the battle system's status move handler
            if hasattr(battle_cog, '_handle_status_move'):
                # Create mock battle data for testing
                mock_battle_data = {
                    'challenger': {'pokemon': {'name': 'TestMon', 'level': 50, 'current_hp': 100}},
                    'opponent': {'pokemon': {'name': 'TestMon2', 'level': 50, 'current_hp': 100}}
                }
                mock_attacker = {'pokemon': {'name': 'TestMon', 'level': 50, 'current_hp': 100}, 'stats': {}}
                mock_defender = {'pokemon': {'name': 'TestMon2', 'level': 50, 'current_hp': 100}, 'stats': {}}
                
                # Check if move is in MOVES_DATA
                if move_name not in MOVES_DATA:
                    return False
                    
                move_data = MOVES_DATA[move_name]
                
                # For status moves, check if they're handled in _handle_status_move
                if category == 'status_moves' and move_data['category'] == 'status':
                    # Check if move is mentioned in the status move handler source
                    import inspect
                    source = inspect.getsource(battle_cog._handle_status_move)
                    return move_name in source or move_name.replace('_', ' ') in source
                    
                # For other categories, check if they're handled in use_move or _handle_status_move
                elif category in ['fixed_damage_moves', 'self_faint_moves', 'ohko_moves', 'multi_hit_moves', 'recoil_moves']:
                    source = inspect.getsource(battle_cog._handle_status_move)
                    return move_name in source
                    
                return True  # Assume implemented for regular damage moves
                
        except Exception as e:
            import logging
            logging.warning(f"Error checking move implementation for {move_name}: {e}")
            return False
            
        return False
        
    @app_commands.command(name="testmove", description="Test a specific move implementation (Admin only)")
    async def test_move(self, interaction: discord.Interaction, move_name: str):
        # Check admin permissions
        import os
        admin_user_id = int(os.getenv('ADMIN_USER_ID', 0)) if os.getenv('ADMIN_USER_ID') else 0
        if interaction.user.id != admin_user_id:
            await interaction.response.send_message("This command is for administrators only!", ephemeral=True)
            return
            
        move_name = move_name.lower().replace(' ', '_')
        
        if move_name not in MOVES_DATA:
            await interaction.response.send_message(f"Move '{move_name}' not found in move database!", ephemeral=True)
            return
            
        move_data = MOVES_DATA[move_name]
        
        embed = discord.Embed(title=f"Move Test: {move_name.replace('_', ' ').title()}", color=0x3498db)
        embed.add_field(name="Type", value=move_data['type'], inline=True)
        embed.add_field(name="Category", value=move_data['category'], inline=True)
        embed.add_field(name="Power", value=move_data['power'], inline=True)
        embed.add_field(name="Accuracy", value=f"{move_data['accuracy']}%", inline=True)
        embed.add_field(name="PP", value=move_data['pp'], inline=True)
        
        # Check implementation status
        battle_cog = self.bot.get_cog('Battle')
        if battle_cog:
            is_implemented = False
            for category, moves in self.required_move_implementations.items():
                if move_name in moves:
                    is_implemented = self._check_move_implementation(battle_cog, move_name, category)
                    break
            else:
                is_implemented = True  # Assume regular damage moves are implemented
                
            embed.add_field(
                name="Implementation Status", 
                value="✅ Implemented" if is_implemented else "❌ Not Implemented", 
                inline=True
            )
        else:
            embed.add_field(name="Implementation Status", value="❓ Battle system not loaded", inline=True)
            
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(MoveValidatorV2(bot))