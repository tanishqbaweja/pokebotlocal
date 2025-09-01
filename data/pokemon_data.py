POKEMON_DATA = {
    1: {"name": "Bulbasaur", "type1": "Grass", "type2": "Poison", "base_hp": 45, "base_attack": 49, "base_defense": 49, "base_special": 65, "base_speed": 45, "exp_group": "medium_slow", "rarity": "common"},
    2: {"name": "Ivysaur", "type1": "Grass", "type2": "Poison", "base_hp": 60, "base_attack": 62, "base_defense": 63, "base_special": 80, "base_speed": 60, "exp_group": "medium_slow", "rarity": "uncommon"},
    3: {"name": "Venusaur", "type1": "Grass", "type2": "Poison", "base_hp": 80, "base_attack": 82, "base_defense": 83, "base_special": 100, "base_speed": 80, "exp_group": "medium_slow", "rarity": "rare"},
    4: {"name": "Charmander", "type1": "Fire", "type2": None, "base_hp": 39, "base_attack": 52, "base_defense": 43, "base_special": 60, "base_speed": 65, "exp_group": "medium_slow", "rarity": "common"},
    5: {"name": "Charmeleon", "type1": "Fire", "type2": None, "base_hp": 58, "base_attack": 64, "base_defense": 58, "base_special": 80, "base_speed": 80, "exp_group": "medium_slow", "rarity": "uncommon"},
    6: {"name": "Charizard", "type1": "Fire", "type2": "Flying", "base_hp": 78, "base_attack": 84, "base_defense": 78, "base_special": 109, "base_speed": 100, "exp_group": "medium_slow", "rarity": "rare"},
    7: {"name": "Squirtle", "type1": "Water", "type2": None, "base_hp": 44, "base_attack": 48, "base_defense": 65, "base_special": 50, "base_speed": 43, "exp_group": "medium_slow", "rarity": "common"},
    8: {"name": "Wartortle", "type1": "Water", "type2": None, "base_hp": 59, "base_attack": 63, "base_defense": 80, "base_special": 65, "base_speed": 58, "exp_group": "medium_slow", "rarity": "uncommon"},
    9: {"name": "Blastoise", "type1": "Water", "type2": None, "base_hp": 79, "base_attack": 83, "base_defense": 100, "base_special": 85, "base_speed": 78, "exp_group": "medium_slow", "rarity": "rare"},
    10: {"name": "Caterpie", "type1": "Bug", "type2": None, "base_hp": 45, "base_attack": 30, "base_defense": 35, "base_special": 20, "base_speed": 45, "exp_group": "medium_fast", "rarity": "common"},
    16: {"name": "Pidgey", "type1": "Normal", "type2": "Flying", "base_hp": 40, "base_attack": 45, "base_defense": 40, "base_special": 35, "base_speed": 56, "exp_group": "medium_slow", "rarity": "common"},
    18: {"name": "Pidgeot", "type1": "Normal", "type2": "Flying", "base_hp": 83, "base_attack": 80, "base_defense": 75, "base_special": 70, "base_speed": 101, "exp_group": "medium_slow", "rarity": "rare"},
    19: {"name": "Rattata", "type1": "Normal", "type2": None, "base_hp": 30, "base_attack": 56, "base_defense": 35, "base_special": 25, "base_speed": 72, "exp_group": "medium_fast", "rarity": "common"},
    25: {"name": "Pikachu", "type1": "Electric", "type2": None, "base_hp": 35, "base_attack": 55, "base_defense": 40, "base_special": 50, "base_speed": 90, "exp_group": "medium_fast", "rarity": "uncommon"},
    26: {"name": "Raichu", "type1": "Electric", "type2": None, "base_hp": 60, "base_attack": 90, "base_defense": 55, "base_special": 90, "base_speed": 110, "exp_group": "medium_fast", "rarity": "uncommon"},
    59: {"name": "Arcanine", "type1": "Fire", "type2": None, "base_hp": 90, "base_attack": 110, "base_defense": 80, "base_special": 100, "base_speed": 95, "exp_group": "slow", "rarity": "rare"},
    65: {"name": "Alakazam", "type1": "Psychic", "type2": None, "base_hp": 55, "base_attack": 50, "base_defense": 45, "base_special": 135, "base_speed": 120, "exp_group": "medium_slow", "rarity": "rare"},
    74: {"name": "Geodude", "type1": "Rock", "type2": "Ground", "base_hp": 40, "base_attack": 80, "base_defense": 100, "base_special": 30, "base_speed": 20, "exp_group": "medium_slow", "rarity": "common"},
    95: {"name": "Onix", "type1": "Rock", "type2": "Ground", "base_hp": 35, "base_attack": 45, "base_defense": 160, "base_special": 30, "base_speed": 70, "exp_group": "medium_fast", "rarity": "uncommon"},
    100: {"name": "Voltorb", "type1": "Electric", "type2": None, "base_hp": 40, "base_attack": 30, "base_defense": 50, "base_special": 55, "base_speed": 100, "exp_group": "medium_fast", "rarity": "uncommon"},
    112: {"name": "Rhydon", "type1": "Ground", "type2": "Rock", "base_hp": 105, "base_attack": 130, "base_defense": 120, "base_special": 45, "base_speed": 40, "exp_group": "slow", "rarity": "rare"},
    120: {"name": "Staryu", "type1": "Water", "type2": None, "base_hp": 30, "base_attack": 45, "base_defense": 55, "base_special": 70, "base_speed": 85, "exp_group": "slow", "rarity": "uncommon"},
    121: {"name": "Starmie", "type1": "Water", "type2": "Psychic", "base_hp": 60, "base_attack": 75, "base_defense": 85, "base_special": 100, "base_speed": 115, "exp_group": "slow", "rarity": "rare"},
    130: {"name": "Gyarados", "type1": "Water", "type2": "Flying", "base_hp": 95, "base_attack": 125, "base_defense": 79, "base_special": 60, "base_speed": 81, "exp_group": "slow", "rarity": "rare"},
    131: {"name": "Lapras", "type1": "Water", "type2": "Ice", "base_hp": 130, "base_attack": 85, "base_defense": 80, "base_special": 85, "base_speed": 60, "exp_group": "slow", "rarity": "rare"},
    143: {"name": "Snorlax", "type1": "Normal", "type2": None, "base_hp": 160, "base_attack": 110, "base_defense": 65, "base_special": 65, "base_speed": 30, "exp_group": "slow", "rarity": "rare"},
    144: {"name": "Articuno", "type1": "Ice", "type2": "Flying", "base_hp": 90, "base_attack": 85, "base_defense": 100, "base_special": 95, "base_speed": 85, "exp_group": "slow", "rarity": "legendary"},
    145: {"name": "Zapdos", "type1": "Electric", "type2": "Flying", "base_hp": 90, "base_attack": 90, "base_defense": 85, "base_special": 125, "base_speed": 100, "exp_group": "slow", "rarity": "legendary"},
    146: {"name": "Moltres", "type1": "Fire", "type2": "Flying", "base_hp": 90, "base_attack": 100, "base_defense": 90, "base_special": 125, "base_speed": 90, "exp_group": "slow", "rarity": "legendary"},
    147: {"name": "Dratini", "type1": "Dragon", "type2": None, "base_hp": 41, "base_attack": 64, "base_defense": 45, "base_special": 50, "base_speed": 50, "exp_group": "slow", "rarity": "rare"},
    150: {"name": "Mewtwo", "type1": "Psychic", "type2": None, "base_hp": 106, "base_attack": 110, "base_defense": 90, "base_special": 154, "base_speed": 130, "exp_group": "slow", "rarity": "legendary"},
    151: {"name": "Mew", "type1": "Psychic", "type2": None, "base_hp": 100, "base_attack": 100, "base_defense": 100, "base_special": 100, "base_speed": 100, "exp_group": "medium_slow", "rarity": "legendary"}
}

RARITY_WEIGHTS = {
    "common": 60,
    "uncommon": 30,
    "rare": 9,
    "legendary": 1
}

POKEBALL_RATES = {
    "pokeball": {"common": 0.45, "uncommon": 0.25, "rare": 0.10, "legendary": 0.03},
    "greatball": {"common": 0.675, "uncommon": 0.375, "rare": 0.15, "legendary": 0.045},
    "ultraball": {"common": 0.90, "uncommon": 0.50, "rare": 0.20, "legendary": 0.06},
    "masterball": {"common": 1.0, "uncommon": 1.0, "rare": 1.0, "legendary": 1.0}
}