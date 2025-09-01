GYM_LEADERS = {
    "brock": {
        "name": "Brock",
        "type": "Rock",
        "badge": "Boulder Badge",
        "reward": 500,
        "team": [
            {"species_id": 74, "level": 12, "moves": ["tackle", "defense_curl", "rock_throw", None]},  # Geodude
            {"species_id": 95, "level": 14, "moves": ["tackle", "screech", "bind", "rock_throw"]}   # Onix
        ]
    },
    "misty": {
        "name": "Misty", 
        "type": "Water",
        "badge": "Cascade Badge",
        "reward": 1000,
        "team": [
            {"species_id": 120, "level": 18, "moves": ["tackle", "water_gun", "harden", "recover"]},  # Staryu
            {"species_id": 121, "level": 21, "moves": ["tackle", "water_gun", "bubble_beam", "recover"]}   # Starmie
        ]
    },
    "surge": {
        "name": "Lt. Surge",
        "type": "Electric", 
        "badge": "Thunder Badge",
        "reward": 1500,
        "team": [
            {"species_id": 100, "level": 21, "moves": ["tackle", "sonic_boom", "screech", "thunder_wave"]}, # Voltorb
            {"species_id": 25, "level": 18, "moves": ["thunder_shock", "growl", "thunder_wave", "quick_attack"]}, # Pikachu
            {"species_id": 26, "level": 24, "moves": ["thunder_shock", "thunderbolt", "thunder_wave", "seismic_toss"]}  # Raichu
        ]
    },
    "erika": {
        "name": "Erika",
        "type": "Grass",
        "badge": "Rainbow Badge", 
        "reward": 2000,
        "team": [
            {"species_id": 71, "level": 29, "moves": ["vine_whip", "acid", "sleep_powder", "razor_leaf"]},   # Victreebel
            {"species_id": 114, "level": 24, "moves": ["vine_whip", "bind", "poison_powder", "growth"]}, # Tangela
            {"species_id": 45, "level": 29, "moves": ["petal_dance", "poison_powder", "sleep_powder", "acid"]}   # Vileplume
        ]
    },
    "koga": {
        "name": "Koga",
        "type": "Poison",
        "badge": "Soul Badge",
        "reward": 2500, 
        "team": [
            {"species_id": 109, "level": 37, "moves": ["sludge", "smog", "toxic", "self_destruct"]},      # Koffing
            {"species_id": 89, "level": 39, "moves": ["sludge", "poison_gas", "minimize", "acid_armor"]},    # Muk
            {"species_id": 109, "level": 37, "moves": ["sludge", "smokescreen", "toxic", "explosion"]},      # Koffing
            {"species_id": 110, "level": 43, "moves": ["sludge", "toxic", "smokescreen", "explosion"]}    # Weezing
        ]
    },
    "sabrina": {
        "name": "Sabrina",
        "type": "Psychic",
        "badge": "Marsh Badge",
        "reward": 3000,
        "team": [
            {"species_id": 64, "level": 38, "moves": ["psychic", "psybeam", "recover", "reflect"]},       # Kadabra
            {"species_id": 122, "level": 37, "moves": ["psychic", "barrier", "light_screen", "substitute"]},      # Mr. Mime
            {"species_id": 49, "level": 38, "moves": ["psychic", "psybeam", "sleep_powder", "stun_spore"]},       # Venomoth
            {"species_id": 65, "level": 43, "moves": ["psychic", "psybeam", "recover", "reflect"]}     # Alakazam
        ]
    },
    "blaine": {
        "name": "Blaine",
        "type": "Fire",
        "badge": "Volcano Badge",
        "reward": 3500,
        "team": [
            {"species_id": 58, "level": 42, "moves": ["flamethrower", "bite", "take_down", "leer"]},        # Growlithe
            {"species_id": 77, "level": 40, "moves": ["ember", "stomp", "fire_spin", "agility"]},      # Ponyta
            {"species_id": 78, "level": 42, "moves": ["flamethrower", "stomp", "fire_spin", "agility"]},   # Rapidash
            {"species_id": 59, "level": 47, "moves": ["flamethrower", "take_down", "leer", "fire_blast"]}    # Arcanine
        ]
    },
    "giovanni": {
        "name": "Giovanni",
        "type": "Ground", 
        "badge": "Earth Badge",
        "reward": 4000,
        "team": [
            {"species_id": 111, "level": 45, "moves": ["horn_attack", "stomp", "tail_whip", "fury_attack"]}, # Rhyhorn
            {"species_id": 51, "level": 42, "moves": ["dig", "slash", "sand_attack", "earthquake"]}, # Dugtrio
            {"species_id": 31, "level": 43, "moves": ["body_slam", "poison_sting", "tail_whip", "earthquake"]},    # Nidoqueen
            {"species_id": 34, "level": 45, "moves": ["thrash", "horn_attack", "poison_sting", "earthquake"]},    # Nidoking
            {"species_id": 112, "level": 50, "moves": ["horn_drill", "take_down", "tail_whip", "earthquake"]} # Rhydon
        ]
    }
}

ELITE_FOUR = {
    "lorelei": {
        "name": "Lorelei",
        "type": "Ice",
        "reward": 5000,
        "team": [
            {"species_id": 87, "level": 54, "moves": ["ice_beam", "aurora_beam", "rest", "take_down"]},   # Dewgong
            {"species_id": 91, "level": 53, "moves": ["ice_beam", "clamp", "aurora_beam", "spike_cannon"]},   # Cloyster
            {"species_id": 80, "level": 54, "moves": ["psychic", "surf", "amnesia", "rest"]},   # Slowbro
            {"species_id": 124, "level": 56, "moves": ["ice_beam", "psychic", "lovely_kiss", "blizzard"]},       # Jynx
            {"species_id": 131, "level": 56, "moves": ["ice_beam", "surf", "psychic", "confuse_ray"]}   # Lapras
        ]
    },
    "bruno": {
        "name": "Bruno", 
        "type": "Fighting",
        "reward": 5000,
        "team": [
            {"species_id": 95, "level": 53, "moves": ["rock_slide", "bind", "harden", "rage"]},      # Onix
            {"species_id": 107, "level": 55, "moves": ["ice_punch", "fire_punch", "thunder_punch", "counter"]},       # Hitmonchan
            {"species_id": 106, "level": 55, "moves": ["mega_kick", "hi_jump_kick", "focus_energy", "seismic_toss"]},       # Hitmonlee
            {"species_id": 95, "level": 56, "moves": ["earthquake", "rock_slide", "bind", "explosion"]},      # Onix
            {"species_id": 68, "level": 58, "moves": ["karate_chop", "seismic_toss", "submission", "focus_energy"]}   # Machamp
        ]
    },
    "agatha": {
        "name": "Agatha",
        "type": "Ghost", 
        "reward": 5000,
        "team": [
            {"species_id": 92, "level": 56, "moves": ["lick", "confuse_ray", "night_shade", "hypnosis"]},        # Gastly
            {"species_id": 42, "level": 56, "moves": ["wing_attack", "confuse_ray", "toxic", "haze"]},        # Golbat
            {"species_id": 93, "level": 55, "moves": ["lick", "confuse_ray", "night_shade", "hypnosis"]},        # Haunter
            {"species_id": 94, "level": 58, "moves": ["lick", "confuse_ray", "night_shade", "dream_eater"]},  # Gengar
            {"species_id": 94, "level": 60, "moves": ["psychic", "confuse_ray", "night_shade", "hypnosis"]}   # Gengar
        ]
    },
    "lance": {
        "name": "Lance",
        "type": "Dragon",
        "reward": 5000, 
        "team": [
            {"species_id": 130, "level": 58, "moves": ["hydro_pump", "leer", "hyper_beam", "dragon_rage"]},  # Gyarados
            {"species_id": 142, "level": 60, "moves": ["wing_attack", "agility", "supersonic", "hyper_beam"]},       # Aerodactyl
            {"species_id": 148, "level": 56, "moves": ["dragon_rage", "leer", "agility", "hyper_beam"]},       # Dragonair
            {"species_id": 148, "level": 56, "moves": ["bubble_beam", "dragon_rage", "leer", "thunder_wave"]},       # Dragonair
            {"species_id": 149, "level": 62, "moves": ["hyper_beam", "fire_blast", "blizzard", "thunder"]}  # Dragonite
        ]
    }
}

CHAMPION = {
    "blue": {
        "name": "Champion Blue",
        "reward": 10000,
        "team": [
            {"species_id": 18, "level": 61, "moves": ["wing_attack", "mirror_move", "sky_attack", "whirlwind"]}, # Pidgeot
            {"species_id": 65, "level": 59, "moves": ["psychic", "recover", "reflect", "psybeam"]},         # Alakazam
            {"species_id": 112, "level": 61, "moves": ["earthquake", "horn_drill", "rock_slide", "substitute"]},  # Rhydon
            {"species_id": 130, "level": 61, "moves": ["surf", "hyper_beam", "fire_blast", "thunder"]},   # Gyarados
            {"species_id": 59, "level": 61, "moves": ["fire_blast", "body_slam", "reflect", "rest"]},       # Arcanine
            {"species_id": 3, "level": 63, "moves": ["razor_leaf", "sleep_powder", "body_slam", "frenzy_plant"]}     # Venusaur
        ]
    }
}