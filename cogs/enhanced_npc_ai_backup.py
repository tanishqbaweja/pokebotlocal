"""
Enhanced NPC AI system for Pokémon battles with strategic decision making.
This module provides advanced AI behaviors for gym leaders, Elite Four, and champion.
"""

import random
from data.complete_moves_data import COMPLETE_MOVES_DATA as MOVES_DATA
from data.complete_pokemon_data import COMPLETE_POKEMON_DATA as POKEMON_DATA
from data.moves_data import TYPE_EFFECTIVENESS

class EnhancedNPCAI:
    """
    Advanced AI system for NPC battles with strategic thinking.
    """
    
    def __init__(self, battle_data, npc_data):
        self.battle_data = battle_data
        self.npc_data = npc_data
        self.player_data = battle_data['challenger'] if battle_data['challenger']['id'] > 0 else battle_data['opponent']
        
    def choose_move(self, valid_moves):
        """
        Main method to choose the best move using strategic AI.
        Returns the move name that the NPC should use.
        """
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
        npc_pokemon = self.npc_data['pokemon']
        player_pokemon = self.player_data['pokemon']
        
        score = 0
        
        # Base scoring for different move types
        if move['category'] == 'physical' or move['category'] == 'special':
            score = self._score_damage_move(move_name, move)
        elif move['category'] == 'status':
            score = self._score_status_move(move_name, move)
            
        # Apply situational modifiers
        score = self._apply_situational_modifiers(move_name, move, score)
        
        return max(0, score)  # Ensure non-negative scores
    
    def _score_damage_move(self, move_name, move):
        """Score damage-dealing moves based on effectiveness and power."""
        if move['power'] == 0:
            return 0
            
        base_score = move['power']
        
        # Type effectiveness calculation
        effectiveness = self._calculate_type_effectiveness(move)
        if effectiveness >= 2.0:
            base_score += 60  # Super effective bonus
        elif effectiveness <= 0.5:
            base_score -= 30  # Not very effective penalty
        elif effectiveness == 0:
            return 0  # No effect
            
        # STAB (Same Type Attack Bonus) consideration
        npc_species = POKEMON_DATA[self.npc_data['pokemon']['species_id']]
        if (move['type'].lower() == npc_species['type1'].lower() or 
            (npc_species.get('type2') and move['type'].lower() == npc_species['type2'].lower())):
            base_score += 20  # STAB bonus
            
        # Player HP consideration
        player_hp_percent = self._get_hp_percentage(self.player_data['pokemon'])
        if player_hp_percent < 0.3 and move['power'] >= 80:
            base_score += 50  # Go for KO when opponent is low
        elif player_hp_percent > 0.8 and move['power'] < 60:
            base_score -= 20  # Don't use weak moves on healthy opponents
            
        # Accuracy consideration
        if move['accuracy'] < 100:
            penalty = (100 - move['accuracy']) // 10
            base_score -= penalty
            
        return base_score
    
    def _score_status_move(self, move_name, move):
        """Score status moves based on current battle situation."""
        npc_hp_percent = self._get_hp_percentage(self.npc_data['pokemon'])
        player_hp_percent = self._get_hp_percentage(self.player_data['pokemon'])
        
        # Healing moves
        if move_name in ['recover', 'rest', 'soft_boiled']:
            if npc_hp_percent < 0.25:
                return 95  # Critical healing
            elif npc_hp_percent < 0.5:
                return 60  # Moderate healing priority
            else:
                return 10  # Low priority when healthy
                
        # Stat boosting moves
        if move_name in ['swords_dance', 'agility', 'amnesia', 'barrier', 'harden', 'defense_curl', 'growth']:
            if npc_hp_percent > 0.6 and not self.npc_data.get('status'):
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
        if move_name in ['sleep_powder', 'thunder_wave', 'toxic', 'poison_powder', 'stun_spore', 'hypnosis', 'sing']:
            if not self.player_data.get('status'):
                # Prioritize sleep and paralysis
                if move_name in ['sleep_powder', 'thunder_wave', 'hypnosis']:
                    return 70
                else:
                    return 50
            else:
                return 5  # Don't waste turn on already statused opponent
                
        # Confusion moves
        if move_name in ['confuse_ray', 'supersonic']:
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
        if move_name in ['substitute', 'leech_seed']:
            if move_name == 'substitute' and npc_hp_percent > 0.5:
                return 45
            elif move_name == 'leech_seed' and not self.player_data.get('seeded'):
                return 40
            else:
                return 10
                
        # Default status move score
        return 20
    
    def _apply_situational_modifiers(self, move_name, move, base_score):
        """Apply additional modifiers based on battle situation."""
        modified_score = base_score
        
        # Desperate situation - prioritize high-damage moves
        npc_hp_percent = self._get_hp_percentage(self.npc_data['pokemon'])
        if npc_hp_percent < 0.2 and move['category'] in ['physical', 'special'] and move['power'] >= 100:
            modified_score += 30
            
        # Status effect considerations
        if self.npc_data.get('status') == 'poison' and move_name in ['recover', 'rest']:
            modified_score += 25  # Higher priority for healing when poisoned
            
        # Move-specific bonuses based on NPC type (gym leaders, elite four, etc.)
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
            
        # 70% chance to pick best move, 25% for second best, 5% for third best
        rand = random.randint(1, 100)
        
        if rand <= 70:
            return viable_moves[0][0]
        elif rand <= 95 and len(viable_moves) > 1:
            return viable_moves[1][0]
        elif len(viable_moves) > 2:
            return viable_moves[2][0]
        else:
            return viable_moves[0][0]
    
    def _calculate_type_effectiveness(self, move):
        """Calculate type effectiveness of move against player's Pokemon."""
        effectiveness = 1.0
        player_species = POKEMON_DATA[self.player_data['pokemon']['species_id']]
        
        move_type = move['type'].lower()
        if move_type in TYPE_EFFECTIVENESS:
            # Check type 1
            if player_species['type1'].lower() in TYPE_EFFECTIVENESS[move_type]:
                effectiveness *= TYPE_EFFECTIVENESS[move_type][player_species['type1'].lower()]
            
            # Check type 2 if exists
            if player_species.get('type2'):
                type2 = player_species['type2'].lower()
                if type2 in TYPE_EFFECTIVENESS[move_type]:
                    effectiveness *= TYPE_EFFECTIVENESS[move_type][type2]
                    
        return effectiveness
    
    def _get_hp_percentage(self, pokemon):
        """Calculate HP percentage of a Pokemon."""
        if pokemon['current_hp'] <= 0:
            return 0.0
        
        species = POKEMON_DATA[pokemon['species_id']]
        max_hp = ((species['base_hp'] + pokemon['hp_iv']) * 2 * pokemon['level'] // 100) + pokemon['level'] + 10
        return pokemon['current_hp'] / max_hp
    
    def _get_relevant_stat_for_move(self, move_name):
        """Get the stat that a move affects."""
        stat_map = {
            'swords_dance': 'attack',
            'agility': 'speed',
            'amnesia': 'special',
            'barrier': 'defense',
            'harden': 'defense',
            'defense_curl': 'defense',
            'growth': 'special',
            'growl': 'attack',
            'leer': 'defense',
            'sand_attack': 'accuracy',
            'smokescreen': 'accuracy',
            'screech': 'defense'
        }
        return stat_map.get(move_name, 'attack')
    
    def _get_npc_type_bonus(self, move_name, move):
        """Get bonus score based on NPC type (gym leader specialty, etc.)."""
        # This could be expanded to give gym leaders bonuses for using moves of their type
        # For now, return a small bonus for type-matching moves
        
        npc_pokemon = self.npc_data['pokemon']
        npc_species = POKEMON_DATA[npc_pokemon['species_id']]
        
        if (move['type'].lower() == npc_species['type1'].lower() or 
            (npc_species.get('type2') and move['type'].lower() == npc_species['type2'].lower())):
            return 10  # Small bonus for type-matching moves
            
        return 0

def choose_npc_move_enhanced(battle_data, npc_data, valid_moves):
    """
    Enhanced move selection function for NPCs.
    This function can be called from the battle system.
    """
    ai = EnhancedNPCAI(battle_data, npc_data)
    return ai.choose_move(valid_moves)
