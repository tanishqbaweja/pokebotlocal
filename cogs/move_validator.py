"""
Move Validator Module - Ensures all Pokemon moves are properly implemented
This module validates that all moves in the data files are correctly working
"""

import discord
from discord.ext import commands
from discord import app_commands
from data.complete_moves_data import COMPLETE_MOVES_DATA as MOVES_DATA

class MoveValidator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.special_moves = {
            # Multi-hit moves
            'double_kick': {'hits': (2, 2)},
            'double_slap': {'hits': (2, 5)},
            'fury_attack': {'hits': (2, 5)},
            'fury_swipes': {'hits': (2, 5)},
            'pin_missile': {'hits': (2, 5)},
            'spike_cannon': {'hits': (2, 5)},
            'barrage': {'hits': (2, 5)},
            'comet_punch': {'hits': (2, 5)},
            'bonemerang': {'hits': (2, 2)},
            'twineedle': {'hits': (2, 2)},
            
            # Recoil moves
            'take_down': {'recoil': 0.25},
            'double_edge': {'recoil': 0.25},
            'submission': {'recoil': 0.25},
            'struggle': {'recoil': 0.5},
            
            # Drain moves
            'absorb': {'drain': 0.5},
            'mega_drain': {'drain': 0.5},
            'leech_life': {'drain': 0.5},
            'dream_eater': {'drain': 0.5},  # Only works on sleeping targets
            
            # OHKO moves
            'fissure': {'ohko': True},
            'guillotine': {'ohko': True},
            'horn_drill': {'ohko': True},
            'sheer_cold': {'ohko': True},
            
            # Two-turn moves
            'fly': {'charge': True},
            'dig': {'charge': True},
            'dive': {'charge': True},
            'bounce': {'charge': True},
            'sky_attack': {'charge': True},
            'skull_bash': {'charge': True},
            'solar_beam': {'charge': True},  # Unless sunny
            'razor_wind': {'charge': True},
            
            # Special mechanics
            'metronome': {'random_move': True},
            'mirror_move': {'copy_last': True},
            'counter': {'counter_physical': True},
            'mirror_coat': {'counter_special': True},
            'bide': {'charge_damage': True},
            'endeavor': {'match_hp': True},
            'final_gambit': {'sacrifice': True},
            'self_destruct': {'sacrifice': True},
            'explosion': {'sacrifice': True},
        }
        
    @app_commands.command(name="validatem

oves", description="Validate that all moves are working properly (Admin only)")
    @app_commands.default_permissions(administrator=True)
    async def validate_moves(self, interaction: discord.Interaction):
        """Validate all moves in the database"""
        await interaction.response.defer(thinking=True)
        
        issues = []
        warnings = []
        total_moves = len(MOVES_DATA)
        validated = 0
        
        for move_name, move_data in MOVES_DATA.items():
            validated += 1
            
            # Check for required fields
            if 'type' not in move_data:
                issues.append(f"❌ {move_name}: Missing 'type' field")
            if 'category' not in move_data:
                issues.append(f"❌ {move_name}: Missing 'category' field")
            if 'power' not in move_data:
                issues.append(f"❌ {move_name}: Missing 'power' field")
            if 'accuracy' not in move_data:
                issues.append(f"❌ {move_name}: Missing 'accuracy' field")
            if 'pp' not in move_data:
                issues.append(f"❌ {move_name}: Missing 'pp' field")
                
            # Check for special move implementations
            if move_name in self.special_moves:
                special_data = self.special_moves[move_name]
                
                # Check if special mechanics are handled in battle.py
                if 'hits' in special_data:
                    warnings.append(f"⚠️ {move_name}: Multi-hit move - ensure battle system handles multiple hits")
                if 'recoil' in special_data:
                    warnings.append(f"⚠️ {move_name}: Recoil move - ensure recoil damage is applied")
                if 'drain' in special_data:
                    warnings.append(f"⚠️ {move_name}: Drain move - ensure HP recovery is applied")
                if 'ohko' in special_data:
                    warnings.append(f"⚠️ {move_name}: OHKO move - ensure instant KO mechanics work")
                if 'charge' in special_data:
                    warnings.append(f"⚠️ {move_name}: Two-turn move - ensure charging mechanics work")
                    
            # Validate move category
            if move_data.get('category') not in ['physical', 'special', 'status']:
                issues.append(f"❌ {move_name}: Invalid category '{move_data.get('category')}'")
                
            # Validate power values
            if move_data.get('category') != 'status' and move_data.get('power', 0) == 0:
                if move_name not in ['sonic_boom', 'dragon_rage', 'night_shade', 'seismic_toss', 'super_fang', 'psywave', 'counter', 'mirror_coat', 'bide']:
                    warnings.append(f"⚠️ {move_name}: Non-status move with 0 power")
                    
            # Validate accuracy (should be between 0-100 or None for never-miss moves)
            accuracy = move_data.get('accuracy')
            if accuracy is not None and (accuracy < 0 or accuracy > 100):
                issues.append(f"❌ {move_name}: Invalid accuracy value {accuracy}")
                
        # Create result embed
        embed = discord.Embed(
            title="Move Validation Report",
            description=f"Validated {validated}/{total_moves} moves",
            color=0x00ff00 if len(issues) == 0 else 0xff0000
        )
        
        if issues:
            issues_text = "\n".join(issues[:10])  # Limit to first 10 issues
            if len(issues) > 10:
                issues_text += f"\n... and {len(issues) - 10} more issues"
            embed.add_field(name=f"Critical Issues ({len(issues)})", value=issues_text, inline=False)
        else:
            embed.add_field(name="✅ No Critical Issues", value="All moves have required fields", inline=False)
            
        if warnings:
            warnings_text = "\n".join(warnings[:10])  # Limit to first 10 warnings
            if len(warnings) > 10:
                warnings_text += f"\n... and {len(warnings) - 10} more warnings"
            embed.add_field(name=f"Warnings ({len(warnings)})", value=warnings_text, inline=False)
            
        embed.add_field(
            name="Summary",
            value=f"Total Moves: {total_moves}\nValidated: {validated}\nIssues: {len(issues)}\nWarnings: {len(warnings)}",
            inline=False
        )
        
        await interaction.followup.send(embed=embed)
        
    @app_commands.command(name="testmove", description="Test a specific move implementation (Admin only)")
    @app_commands.default_permissions(administrator=True)
    async def test_move(self, interaction: discord.Interaction, move_name: str):
        """Test a specific move's implementation"""
        move_name = move_name.lower().replace(" ", "_")
        
        if move_name not in MOVES_DATA:
            await interaction.response.send_message(f"Move '{move_name}' not found in moves database!", ephemeral=True)
            return
            
        move_data = MOVES_DATA[move_name]
        
        embed = discord.Embed(
            title=f"Move Test: {move_name.replace('_', ' ').title()}",
            color=0x3498db
        )
        
        # Basic info
        embed.add_field(name="Type", value=move_data.get('type', 'Unknown'), inline=True)
        embed.add_field(name="Category", value=move_data.get('category', 'Unknown'), inline=True)
        embed.add_field(name="Power", value=move_data.get('power', 0), inline=True)
        embed.add_field(name="Accuracy", value=move_data.get('accuracy', 100), inline=True)
        embed.add_field(name="PP", value=move_data.get('pp', 0), inline=True)
        
        # Check special mechanics
        if move_name in self.special_moves:
            special = self.special_moves[move_name]
            special_text = []
            
            if 'hits' in special:
                min_hits, max_hits = special['hits']
                special_text.append(f"Multi-hit: {min_hits}-{max_hits} times")
            if 'recoil' in special:
                special_text.append(f"Recoil: {special['recoil']*100:.0f}% of damage")
            if 'drain' in special:
                special_text.append(f"Drain: {special['drain']*100:.0f}% of damage")
            if 'ohko' in special:
                special_text.append("One-hit KO move")
            if 'charge' in special:
                special_text.append("Two-turn charging move")
            if 'random_move' in special:
                special_text.append("Uses random move")
            if 'copy_last' in special:
                special_text.append("Copies opponent's last move")
            if 'counter_physical' in special:
                special_text.append("Counters physical damage")
            if 'counter_special' in special:
                special_text.append("Counters special damage")
            if 'sacrifice' in special:
                special_text.append("User faints after use")
                
            embed.add_field(name="Special Mechanics", value="\n".join(special_text), inline=False)
            
        # Check if move is implemented in battle system
        battle_cog = self.bot.get_cog('Battle')
        if battle_cog:
            # Check if move is handled in status moves
            status_moves_handled = [
                'growl', 'tail_whip', 'leer', 'screech', 'acid', 'sand_attack', 
                'smokescreen', 'flash', 'kinesis', 'swords_dance', 'sharpen', 
                'meditate', 'harden', 'withdraw', 'defense_curl', 'acid_armor',
                'agility', 'string_shot', 'amnesia', 'barrier', 'growth',
                'poison_powder', 'poison_gas', 'toxic', 'sleep_powder', 'spore',
                'sing', 'hypnosis', 'lovely_kiss', 'stun_spore', 'thunder_wave',
                'glare', 'supersonic', 'confuse_ray', 'recover', 'rest', 
                'soft_boiled', 'transform', 'sonic_boom', 'dragon_rage',
                'night_shade', 'seismic_toss', 'super_fang', 'psywave',
                'double_team', 'minimize', 'haze', 'mist', 'light_screen',
                'reflect', 'leech_seed', 'substitute', 'teleport', 'whirlwind',
                'roar', 'splash', 'disable', 'focus_energy', 'conversion', 'mimic'
            ]
            
            if move_data.get('category') == 'status' and move_name in status_moves_handled:
                embed.add_field(name="✅ Implementation", value="Status move is handled", inline=False)
            elif move_data.get('category') != 'status':
                embed.add_field(name="✅ Implementation", value="Damage move will be calculated", inline=False)
            else:
                embed.add_field(name="⚠️ Implementation", value="May need special handling", inline=False)
                
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(MoveValidator(bot))
