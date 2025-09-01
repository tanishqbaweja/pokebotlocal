-- Pokemon Bot Database Schema

-- Users table - stores trainer information
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(32) NOT NULL,
    money INTEGER DEFAULT 5000,
    badges INTEGER DEFAULT 0,
    default_pokeball VARCHAR(20) DEFAULT 'pokeball',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pokemon species data
CREATE TABLE pokemon_species (
    id INTEGER PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    type1 VARCHAR(10) NOT NULL,
    type2 VARCHAR(10),
    base_hp INTEGER NOT NULL,
    base_attack INTEGER NOT NULL,
    base_defense INTEGER NOT NULL,
    base_special INTEGER NOT NULL,
    base_speed INTEGER NOT NULL,
    exp_group VARCHAR(20) NOT NULL,
    rarity VARCHAR(10) NOT NULL
);

-- Individual Pokemon instances
CREATE TABLE pokemon (
    id SERIAL PRIMARY KEY,
    owner_id BIGINT REFERENCES users(user_id),
    species_id INTEGER REFERENCES pokemon_species(id),
    level INTEGER DEFAULT 5,
    experience INTEGER DEFAULT 0,
    hp_iv INTEGER DEFAULT 0,
    attack_iv INTEGER DEFAULT 0,
    defense_iv INTEGER DEFAULT 0,
    special_iv INTEGER DEFAULT 0,
    speed_iv INTEGER DEFAULT 0,
    current_hp INTEGER,
    is_shiny BOOLEAN DEFAULT FALSE,
    in_party BOOLEAN DEFAULT FALSE,
    party_position INTEGER,
    move1 VARCHAR(20),
    move2 VARCHAR(20),
    move3 VARCHAR(20),
    move4 VARCHAR(20),
    status_condition VARCHAR(10),
    caught_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User inventory
CREATE TABLE user_inventory (
    user_id BIGINT REFERENCES users(user_id),
    item_name VARCHAR(30),
    quantity INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, item_name)
);

-- Server configuration
CREATE TABLE server_config (
    guild_id BIGINT PRIMARY KEY,
    spawn_channels BIGINT[],
    message_count INTEGER DEFAULT 0,
    messages_until_spawn INTEGER DEFAULT 15
);

-- Active trades
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    requester_id BIGINT REFERENCES users(user_id),
    target_id BIGINT REFERENCES users(user_id),
    pokemon_offered INTEGER REFERENCES pokemon(id),
    pokemon_requested INTEGER REFERENCES pokemon(id),
    status VARCHAR(10) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP + INTERVAL '5 minutes'
);

-- Battle states
CREATE TABLE battles (
    id SERIAL PRIMARY KEY,
    challenger_id BIGINT REFERENCES users(user_id),
    opponent_id BIGINT REFERENCES users(user_id),
    challenger_pokemon INTEGER REFERENCES pokemon(id),
    opponent_pokemon INTEGER REFERENCES pokemon(id),
    turn_user_id BIGINT,
    battle_data JSONB,
    status VARCHAR(10) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_pokemon_owner ON pokemon(owner_id);
CREATE INDEX idx_pokemon_party ON pokemon(owner_id, in_party);
CREATE INDEX idx_trades_active ON trades(status, expires_at);
CREATE INDEX idx_battles_active ON battles(status);