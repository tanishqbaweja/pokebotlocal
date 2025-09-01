-- Populate pokemon_species table with Gen 1 data
INSERT INTO pokemon_species (id, name, type1, type2, base_hp, base_attack, base_defense, base_special, base_speed, exp_group, rarity) VALUES
(1, 'Bulbasaur', 'Grass', 'Poison', 45, 49, 49, 65, 45, 'medium_slow', 'common'),
(2, 'Ivysaur', 'Grass', 'Poison', 60, 62, 63, 80, 60, 'medium_slow', 'uncommon'),
(3, 'Venusaur', 'Grass', 'Poison', 80, 82, 83, 100, 80, 'medium_slow', 'rare'),
(4, 'Charmander', 'Fire', NULL, 39, 52, 43, 60, 65, 'medium_slow', 'common'),
(5, 'Charmeleon', 'Fire', NULL, 58, 64, 58, 80, 80, 'medium_slow', 'uncommon'),
(6, 'Charizard', 'Fire', 'Flying', 78, 84, 78, 109, 100, 'medium_slow', 'rare'),
(7, 'Squirtle', 'Water', NULL, 44, 48, 65, 50, 43, 'medium_slow', 'common'),
(8, 'Wartortle', 'Water', NULL, 59, 63, 80, 65, 58, 'medium_slow', 'uncommon'),
(9, 'Blastoise', 'Water', NULL, 79, 83, 100, 85, 78, 'medium_slow', 'rare'),
(25, 'Pikachu', 'Electric', NULL, 35, 55, 40, 50, 90, 'medium_fast', 'uncommon'),
(150, 'Mewtwo', 'Psychic', NULL, 106, 110, 90, 154, 130, 'slow', 'legendary'),
(151, 'Mew', 'Psychic', NULL, 100, 100, 100, 100, 100, 'medium_slow', 'legendary');