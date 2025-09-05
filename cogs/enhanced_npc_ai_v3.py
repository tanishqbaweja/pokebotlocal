"""
Enhanced NPC AI system for Pokémon battles with strategic decision making.
Version 3 - Comprehensive strategic AI with proper move implementation
"""

import random
from data.complete_moves_data import COMPLETE_MOVES_DATA as MOVES_DATA
from data.complete_pokemon_data import COMPLETE_POKEMON_DATA as POKEMON_DATA
from data.moves_data import TYPE_EFFECTIVENESS

# Strategic constants for better maintainability
SUPER_EFFECTIVE_BONUS = 60
STAB_BONUS = 20
NOT_VERY_EFFECTIVE_PENALTY = 30
CRITICAL_HEAL_THRESHOLD = 0.25
MODERATE_HEAL_THRESHOLD = 0.5
HEALTHY_THRESHOLD = 0.6
LOW_HP_THRESHOLD = 0.3
HIGH_HP_THRESHOLD = 0.8

class EnhancedNPCAIv3:
    """
    Advanced AI system for NPC battles with comprehensive strategic thinking.
    """
    
    def __init__(self, battle_data, npc_data):
        self.battle_data = battle_data
        self.npc_data = npc_data
        self.player_data = battle_data['challenger'] if battle_data['challenger']['id'] > 0 else battle_data['opponent']
        self.turn_count = battle_data.get('turn_count', 0)
        
        # Cache frequently accessed data
        self.npc_pokemon = npc_data['pokemon']
        self.player_pokemon = self.player_data['pokemon']
        self.npc_species = POKEMON_DATA.get(self.npc_pokemon['species_id'], {})
        self.player_species = POKEMON_DATA.get(self.player_pokemon['species_id'], {})
        
    def choose_move(self, valid_moves):
        """
        Main method to choose the best move using strategic AI.
        Returns the move name that the NPC should use.
        """
        if not valid_moves:
            return 'tackle'  # Fallback
            
        move_scores = []
        
        for move_name in valid_moves:
            if move_name not in MOVES_DATA:
                continue
                
            move = MOVES_DATA[move_name]
            score = self._evaluate_move(move_name, move)
            move_scores.append((move_name, score))
            
        # Sort by score (highest first)
        move_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Strategic selection with weighted randomness
        return self._select_move_strategically(move_scores, valid_moves)
    
    def _evaluate_move(self, move_name, move):
        """
        Evaluate a move and assign a strategic score.
        Higher scores indicate better moves to use.
        """
        score = 0
        
        # Base scoring for different move types
        if move['category'] in ['physical', 'special']:
            score = self._score_damage_move(move_name, move)
        elif move['category'] == 'status':
            score = self._score_status_move(move_name, move)
            
        # Apply situational modifiers
        score = self._apply_situational_modifiers(move_name, move, score)
        
        return max(0, score)  # Ensure non-negative scores
    
    def _score_damage_move(self, move_name, move):
        """Score damage-dealing moves based on effectiveness and power."""
        if move['power'] == 0:
            return self._score_special_damage_move(move_name)
            
        base_score = move['power']
        
        # Type effectiveness calculation
        effectiveness = self._calculate_type_effectiveness(move)
        if effectiveness >= 2.0:
            base_score += SUPER_EFFECTIVE_BONUS
        elif effectiveness <= 0.5:
            base_score -= NOT_VERY_EFFECTIVE_PENALTY
        elif effectiveness == 0:
            return 0  # No effect
            
        # STAB (Same Type Attack Bonus) consideration
        if self._has_stab(move):
            base_score += STAB_BONUS
            
        # Player HP consideration
        player_hp_percent = self._get_hp_percentage(self.player_pokemon)
        if player_hp_percent < LOW_HP_THRESHOLD and move['power'] >= 80:
            base_score += 50  # Go for KO when opponent is low
        elif player_hp_percent > HIGH_HP_THRESHOLD and move['power'] < 60:
            base_score -= 20  # Don't use weak moves on healthy opponents
            
        # Accuracy consideration
        if move['accuracy'] < 100:
            penalty = (100 - move['accuracy']) // 10
            base_score -= penalty
            
        # Priority move bonus in critical situations
        if self._is_priority_move(move_name) and player_hp_percent < 0.25:
            base_score += 35
                
        return base_score
    
    def _score_special_damage_move(self, move_name):
        """Score special damage moves like OHKO moves, fixed damage moves"""
        if move_name in ['fissure', 'guillotine', 'horn_drill']:
            # OHKO moves - only good if we're higher level
            if self.npc_pokemon['level'] >= self.player_pokemon['level']:
                return 80  # High priority for OHKO
            return 5  # Low priority if can't use effectively
            
        elif move_name in ['sonic_boom', 'dragon_rage', 'night_shade', 'seismic_toss']:
            damage_map = {
                'sonic_boom': 20,
                'dragon_rage': 40,
                'night_shade': self.npc_pokemon['level'],
                'seismic_toss': self.npc_pokemon['level']
            }
            expected_damage = damage_map.get(move_name, 20)
            player_hp = self.player_pokemon['current_hp']
            
            if player_hp <= expected_damage * 1.5:
                return 60  # Good for finishing
            return 30  # Moderate priority
            
        elif move_name in ['selfdestruct', 'explosion']:
            # Only use if we can KO and we're losing badly
            npc_hp_percent = self._get_hp_percentage(self.npc_pokemon)
            if npc_hp_percent < 0.3:
                return 70  # Desperate measure
            return 10  # Low priority otherwise
            
        return 20  # Default for other special moves
    
    def _score_status_move(self, move_name, move):
        """Score status moves based on current battle situation."""
        npc_hp_percent = self._get_hp_percentage(self.npc_pokemon)
        player_hp_percent = self._get_hp_percentage(self.player_pokemon)
        
        # Healing moves
        if move_name in ['recover', 'rest', 'soft_boiled', 'milk_drink', 'moonlight', 'morning_sun', 'synthesis']:
            if npc_hp_percent < CRITICAL_HEAL_THRESHOLD:
                return 95  # Critical healing
            elif npc_hp_percent < MODERATE_HEAL_THRESHOLD:
                return 60  # Moderate healing priority
            else:
                return 10  # Low priority when healthy
                
        # Stat boosting moves
        if move_name in ['swords_dance', 'agility', 'amnesia', 'barrier', 'harden', 'defense_curl', 'growth']:
            if npc_hp_percent > HEALTHY_THRESHOLD and not self.npc_data.get('status'):
                stat_boosts = self.npc_data.get('stats', {})
                relevant_stat = self._get_relevant_stat_for_move(move_name)
                current_boost = stat_boosts.get(relevant_stat, 0)
                
                if current_boost < 2:
                    return 55  # Good opportunity to boost
                elif current_boost < 4:
                    return 25  # Some value in further boosting
                else:
                    return 5   # Already well-boosted
            else:
                return 15  # Low priority when hurt or statused
                
        # Status infliction moves
        if move_name in ['sleep_powder', 'thunder_wave', 'toxic', 'poison_powder', 'stun_spore', 'hypnosis', 'sing', 'spore', 'will_o_wisp']:
            if not self.player_data.get('status'):
                # Prioritize sleep and paralysis
                if move_name in ['sleep_powder', 'thunder_wave', 'hypnosis', 'spore']:
                    return 70
                elif move_name == 'toxic':
                    return 65  # Toxic is very strong
                else:
                    return 50
            else:
                return 5  # Don't waste turn on already statused opponent
                
        # Confusion moves
        if move_name in ['confuse_ray', 'supersonic', 'swagger']:
            if not self.player_data.get('confused'):
                return 40
            else:
                return 5
                
        # Stat reduction moves
        if move_name in ['growl', 'leer', 'sand_attack', 'smokescreen', 'screech']:
            player_stats = self.player_data.get('stats', {})
            relevant_stat = self._get_relevant_stat_for_move(move_name)
            current_reduction = player_stats.get(relevant_stat, 0)
            
            if current_reduction > -3:
                return 30  # Moderate priority for debuffing
            else:
                return 5   # Already well-debuffed
                
        # Set-up moves
        if move_name in ['substitute', 'leech_seed', 'light_screen', 'reflect', 'focus_energy']:
            if move_name == 'substitute' and npc_hp_percent > 0.5:
                return 45
            elif move_name == 'leech_seed' and not self.player_data.get('seeded'):
                return 40
            elif move_name in ['light_screen', 'reflect'] and npc_hp_percent > HEALTHY_THRESHOLD:
                return 35
            elif move_name == 'focus_energy' and not self.npc_data.get('focus_energy'):
                return 30
            else:
                return 10
                
        # Default status move score
        return 20
    
    def _apply_situational_modifiers(self, move_name, move, base_score):
        """Apply additional modifiers based on battle situation."""
        modified_score = base_score
        npc_hp_percent = self._get_hp_percentage(self.npc_pokemon)
        player_hp_percent = self._get_hp_percentage(self.player_pokemon)
        
        # Desperate situation - prioritize high-damage moves
        if npc_hp_percent < 0.2 and move['category'] in ['physical', 'special'] and move['power'] >= 100:
            modified_score += 30
            
        # When both are low HP, prioritize priority moves or quick KO moves
        if npc_hp_percent < 0.3 and player_hp_percent < 0.3:
            if self._is_priority_move(move_name):
                modified_score += 40  # Priority moves are crucial in close battles
            elif move['category'] != 'status' and move['power'] > 0:
                # Calculate if this move can KO
                estimated_damage = self._estimate_damage(move)
                if estimated_damage >= self.player_pokemon['current_hp']:
                    modified_score += 50  # Guaranteed KO
                    
        # Status effect considerations
        if self.npc_data.get('status') == 'poison' and move_name in ['recover', 'rest']:
            modified_score += 25  # Higher priority for healing when poisoned
        elif self.npc_data.get('status') == 'burn' and move['category'] == 'physical':
            modified_score -= 15  # Physical moves are weakened by burn
            
        # Consider field effects
        if self.npc_data.get('seeded'):
            # Being seeded makes stalling less viable
            if move['category'] == 'status' and move_name not in ['recover', 'rest']:
                modified_score -= 10
                
        # Move-specific bonuses based on NPC type
        modified_score += self._get_npc_type_bonus(move_name, move)
        
        return modified_score
    
    def _select_move_strategically(self, move_scores, valid_moves):
        """Select move with strategic randomness to avoid predictability."""
        if not move_scores:
            return random.choice(valid_moves)
            
        # Filter out moves with very low scores
        viable_moves = [m for m in move_scores if m[1] > 0]
        if not viable_moves:
            return random.choice(valid_moves)
            
        # Dynamic strategy based on NPC difficulty level
        npc_id = self.npc_data.get('id', 0)
        if npc_id < 0:
            npc_type = abs(npc_id) // 1000  # 1=gym, 2=elite4, 3=champion
            if npc_type == 3:  # Champion - most strategic
                rand = random.randint(1, 100)
                if rand <= 85:
                    return viable_moves[0][0]
                elif rand <= 97 and len(viable_moves) > 1:
                    return viable_moves[1][0]
                elif len(viable_moves) > 2:
                    return viable_moves[2][0]
            elif npc_type == 2:  # Elite Four - very strategic
                rand = random.randint(1, 100)
                if rand <= 75:
                    return viable_moves[0][0]
                elif rand <= 95 and len(viable_moves) > 1:
                    return viable_moves[1][0]
                elif len(viable_moves) > 2:
                    return viable_moves[2][0]
            else:  # Gym leaders - moderately strategic
                rand = random.randint(1, 100)
                if rand <= 65:
                    return viable_moves[0][0]
                elif rand <= 90 and len(viable_moves) > 1:
                    return viable_moves[1][0]
                elif len(viable_moves) > 2:
                    return viable_moves[2][0]
        else:
            # Default strategy
            rand = random.randint(1, 100)
            if rand <= 70:
                return viable_moves[0][0]
            elif rand <= 95 and len(viable_moves) > 1:
                return viable_moves[1][0]
            elif len(viable_moves) > 2:
                return viable_moves[2][0]
                
        return viable_moves[0][0]
    
    def _calculate_type_effectiveness(self, move):
        """Calculate type effectiveness of move against player's Pokemon."""
        effectiveness = 1.0
        
        move_type = move['type'].lower()
        if move_type in TYPE_EFFECTIVENESS:
            # Check type 1
            if self.player_species['type1'].lower() in TYPE_EFFECTIVENESS[move_type]:
                effectiveness *= TYPE_EFFECTIVENESS[move_type][self.player_species['type1'].lower()]
            
            # Check type 2 if exists
            if self.player_species.get('type2'):
                type2 = self.player_species['type2'].lower()
                if type2 in TYPE_EFFECTIVENESS[move_type]:
                    effectiveness *= TYPE_EFFECTIVENESS[move_type][type2]
                    
        return effectiveness
    
    def _has_stab(self, move):
        """Check if move gets STAB (Same Type Attack Bonus)"""
        move_type = move['type'].lower()
        return (move_type == self.npc_species['type1'].lower() or 
                (self.npc_species.get('type2') and move_type == self.npc_species['type2'].lower()))
    
    def _is_priority_move(self, move_name):
        """Check if move has priority"""
        priority_moves = ['quick_attack', 'mach_punch', 'aqua_jet', 'bullet_punch', 'ice_shard', 'shadow_sneak', 'extreme_speed']
        return move_name in priority_moves
    
    def _estimate_damage(self, move):
        """Estimate damage this move would deal to the player's Pokemon."""
        if move['power'] == 0:
            return 0
            
        # Simplified damage calculation for estimation
        if move['category'] == 'physical':
            attack_stat = self.npc_species['base_attack'] + 50  # Simplified
            defense_stat = self.player_species['base_defense'] + 50
        else:
            attack_stat = self.npc_species['base_special'] + 50
            defense_stat = self.player_species['base_special'] + 50
            
        # Base damage formula
        damage = ((2 * self.npc_pokemon['level'] + 10) / 250) * (attack_stat / defense_stat) * move['power'] + 2
        
        # Type effectiveness
        effectiveness = self._calculate_type_effectiveness(move)
        damage *= effectiveness
        
        # STAB
        if self._has_stab(move):
            damage *= 1.5
            
        # Conservative estimate
        return int(damage * 0.9)
    
    def _get_hp_percentage(self, pokemon):
        """Calculate HP percentage of a Pokemon."""
        if pokemon['current_hp'] <= 0:
            return 0.0
        
        species = POKEMON_DATA.get(pokemon['species_id'], {})
        if not species:
            return 1.0  # Fallback
            
        max_hp = ((species['base_hp'] + pokemon['hp_iv']) * 2 * pokemon['level'] // 100) + pokemon['level'] + 10
        return pokemon['current_hp'] / max_hp
    
    def _get_relevant_stat_for_move(self, move_name):
        """Get the stat that a move affects."""
        stat_map = {
            'swords_dance': 'attack', 'agility': 'speed', 'amnesia': 'special',
            'barrier': 'defense', 'harden': 'defense', 'defense_curl': 'defense',
            'growth': 'special', 'growl': 'attack', 'leer': 'defense',
            'sand_attack': 'accuracy', 'smokescreen': 'accuracy', 'screech': 'defense'
        }
        return stat_map.get(move_name, 'attack')
    
    def _get_npc_type_bonus(self, move_name, move):
        """Get bonus score based on NPC type (gym leader specialty, etc.)."""
        bonus = 0
        
        # Base type-matching bonus
        if self._has_stab(move):
            bonus += 10
            
        # Additional bonuses based on NPC type
        npc_id = self.npc_data.get('id', 0)
        if npc_id < 0:
            npc_type = abs(npc_id) // 1000
            npc_index = abs(npc_id) % 1000
            
            # Gym leaders get extra bonus for their specialty type
            if npc_type == 1:  # Gym leader
                gym_types = ['rock', 'water', 'electric', 'grass', 'poison', 'psychic', 'fire', 'ground']
                if npc_index < len(gym_types):
                    specialty_type = gym_types[npc_index]
                    if move['type'].lower() == specialty_type:
                        bonus += 15
                        
            elif npc_type == 2:  # Elite Four
                elite_types = ['ice', 'fighting', 'ghost', 'dragon']
                if npc_index < len(elite_types):
                    specialty_type = elite_types[npc_index]
                    if move['type'].lower() == specialty_type:
                        bonus += 20
                        
            elif npc_type == 3:  # Champion
                if move['category'] != 'status' and move['power'] > 80:
                    bonus += 5
                type_effectiveness = self._calculate_type_effectiveness(move)
                if type_effectiveness >= 2:
                    bonus += 10
                    
        return bonus

def choose_npc_move_enhanced(battle_data, npc_data, valid_moves):
    """
    Enhanced move selection function for NPCs.
    This function can be called from the battle system.
    """
    ai = EnhancedNPCAIv3(battle_data, npc_data)
    return ai.choose_move(valid_moves)