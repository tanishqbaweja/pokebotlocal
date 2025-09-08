import asyncpg
import asyncio

class Database:
    def __init__(self, database_url):
        self.database_url = database_url
        self.pool = None
        
    async def connect(self):
        self.pool = await asyncpg.create_pool(self.database_url)
        
    async def execute(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
            
    async def fetch(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
            
    async def fetchrow(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
            
    async def fetchval(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)
            
    async def create_user(self, user_id, username):
        await self.execute(
            "INSERT INTO users (user_id, username) VALUES ($1, $2) ON CONFLICT (user_id) DO NOTHING",
            user_id, username
        )
        
    async def get_user(self, user_id):
        return await self.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
        
    async def get_user_pokemon(self, user_id, in_party=None):
        if in_party is None:
            return await self.fetch(
                "SELECT p.*, ps.name, ps.type1, ps.type2 FROM pokemon p "
                "JOIN pokemon_species ps ON p.species_id = ps.id "
                "WHERE p.owner_id = $1 ORDER BY p.party_position NULLS LAST, p.id",
                user_id
            )
        return await self.fetch(
            "SELECT p.*, ps.name, ps.type1, ps.type2 FROM pokemon p "
            "JOIN pokemon_species ps ON p.species_id = ps.id "
            "WHERE p.owner_id = $1 AND p.in_party = $2 "
            "ORDER BY p.party_position",
            user_id, in_party
        )
        
    async def add_pokemon(self, owner_id, species_id, level=5, is_shiny=False):
        # Check Pokemon limit (999)
        total_pokemon = await self.fetchval(
            "SELECT COUNT(*) FROM pokemon WHERE owner_id = $1",
            owner_id
        )
        
        if total_pokemon >= 999:
            return None  # Cannot add more Pokemon
            
        from data.complete_pokemon_data import COMPLETE_POKEMON_DATA as POKEMON_DATA
        species = POKEMON_DATA[species_id]
        
        # Generate random IVs (0-15)
        import random
        ivs = {stat: random.randint(0, 15) for stat in ['hp', 'attack', 'defense', 'special', 'speed']}
        
        # Calculate HP
        hp = ((species['base_hp'] + ivs['hp']) * 2 * level // 100) + level + 10
        
        # Check if party has space
        party_count = await self.fetchval(
            "SELECT COUNT(*) FROM pokemon WHERE owner_id = $1 AND in_party = TRUE",
            owner_id
        )
        
        in_party = party_count < 6
        party_position = party_count + 1 if in_party else None
        
        # Create Pokemon with no moves initially
        pokemon_id = await self.fetchval(
            """INSERT INTO pokemon (owner_id, species_id, level, hp_iv, attack_iv, 
               defense_iv, special_iv, speed_iv, current_hp, is_shiny, in_party, party_position)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12) RETURNING id""",
            owner_id, species_id, level, ivs['hp'], ivs['attack'], ivs['defense'],
            ivs['special'], ivs['speed'], hp, is_shiny, in_party, party_position
        )
        
        return pokemon_id
        
    def _get_moves_for_level(self, species_id, level):
        """Get appropriate moves for a Pokemon at a specific level"""
        from data.complete_moves_data import LEVEL_MOVESETS
        from data.complete_pokemon_data import COMPLETE_POKEMON_DATA
        import json
        
        moves = [None, None, None, None]
        learned_moves = []
        
        # Try to load from levelup_moves.json first
        try:
            with open('levelup_moves.json', 'r') as f:
                levelup_data = json.load(f)
            
            pokemon_data = COMPLETE_POKEMON_DATA.get(species_id)
            if pokemon_data:
                species_name = pokemon_data['name']
                if species_name in levelup_data:
                    for learn_level_str in levelup_data[species_name]:
                        learn_level = int(learn_level_str)
                        if learn_level <= level:
                            move_list = levelup_data[species_name][learn_level_str]
                            if isinstance(move_list, list):
                                # Convert move names to lowercase with underscores
                                converted_moves = [move.lower().replace(' ', '_').replace('-', '_') for move in move_list]
                                learned_moves.extend(converted_moves)
                            else:
                                converted_move = move_list.lower().replace(' ', '_').replace('-', '_')
                                learned_moves.append(converted_move)
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            # Fallback to LEVEL_MOVESETS if JSON loading fails
            if species_id in LEVEL_MOVESETS:
                for learn_level in sorted(LEVEL_MOVESETS[species_id].keys()):
                    if learn_level <= level:
                        move_list = LEVEL_MOVESETS[species_id][learn_level]
                        if isinstance(move_list, list):
                            learned_moves.extend(move_list)
                        else:
                            learned_moves.append(move_list)
        
        # If no moves found or not enough moves, add type-appropriate moves
        if not learned_moves:
            pokemon_data = COMPLETE_POKEMON_DATA[species_id]
            type1 = pokemon_data['type1'].lower()
            
            # Give type-appropriate moves based on Pokemon type
            type_moves = {
                'fire': ['ember', 'tackle', 'leer', 'flamethrower'],
                'water': ['water_gun', 'tackle', 'bubble', 'surf'], 
                'grass': ['vine_whip', 'tackle', 'absorb', 'razor_leaf'],
                'electric': ['thundershock', 'tackle', 'thunder_wave', 'thunderbolt'],
                'psychic': ['confusion', 'teleport', 'psybeam', 'psychic'],
                'fighting': ['karate_chop', 'leer', 'seismic_toss', 'submission'],
                'poison': ['poison_sting', 'tackle', 'acid', 'sludge'],
                'ground': ['scratch', 'sand_attack', 'dig', 'earthquake'],
                'flying': ['peck', 'gust', 'wing_attack', 'drill_peck'],
                'bug': ['string_shot', 'tackle', 'leech_life', 'pin_missile'],
                'rock': ['rock_throw', 'tackle', 'harden', 'rock_slide'],
                'ghost': ['lick', 'confuse_ray', 'night_shade', 'dream_eater'],
                'ice': ['tackle', 'leer', 'ice_beam', 'blizzard'],
                'dragon': ['dragon_rage', 'leer', 'slam', 'hyper_beam'],
                'normal': ['tackle', 'growl', 'quick_attack', 'body_slam']
            }
            
            learned_moves = type_moves.get(type1, type_moves['normal'])
        
        # Determine number of moves based on level
        if level >= 20:
            num_moves = 4
        elif level >= 15:
            num_moves = 3
        else:
            num_moves = 2
        
        # Ensure we have enough moves by padding with type moves if needed
        if len(learned_moves) < num_moves:
            pokemon_data = COMPLETE_POKEMON_DATA[species_id]
            type1 = pokemon_data['type1'].lower()
            type_moves = {
                'fire': ['ember', 'tackle', 'leer', 'flamethrower'],
                'water': ['water_gun', 'tackle', 'bubble', 'surf'], 
                'grass': ['vine_whip', 'tackle', 'absorb', 'razor_leaf'],
                'electric': ['thundershock', 'tackle', 'thunder_wave', 'thunderbolt'],
                'psychic': ['confusion', 'teleport', 'psybeam', 'psychic'],
                'fighting': ['karate_chop', 'leer', 'seismic_toss', 'submission'],
                'poison': ['poison_sting', 'tackle', 'acid', 'sludge'],
                'ground': ['scratch', 'sand_attack', 'dig', 'earthquake'],
                'flying': ['peck', 'gust', 'wing_attack', 'drill_peck'],
                'bug': ['string_shot', 'tackle', 'leech_life', 'pin_missile'],
                'rock': ['rock_throw', 'tackle', 'harden', 'rock_slide'],
                'ghost': ['lick', 'confuse_ray', 'night_shade', 'dream_eater'],
                'ice': ['tackle', 'leer', 'ice_beam', 'blizzard'],
                'dragon': ['dragon_rage', 'leer', 'slam', 'hyper_beam'],
                'normal': ['tackle', 'growl', 'quick_attack', 'body_slam']
            }
            
            fallback_moves = type_moves.get(type1, type_moves['normal'])
            # Add fallback moves until we have enough
            for move in fallback_moves:
                if move not in learned_moves:
                    learned_moves.append(move)
                    if len(learned_moves) >= num_moves:
                        break
            
        # Take the most recent moves up to the limit
        recent_moves = learned_moves[-num_moves:] if len(learned_moves) >= num_moves else learned_moves
        
        # Fill moves array
        for i, move in enumerate(recent_moves):
            if i < 4:  # Safety check
                moves[i] = move
                
        return moves
        
    def get_moves_for_level(self, species_id, level):
        """Public method to get moves for gym/elite four Pokemon"""
        return self._get_moves_for_level(species_id, level)