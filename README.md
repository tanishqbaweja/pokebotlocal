# Professor Byte - Pokemon Generation 1 Discord Bot

A fully-featured Pokemon Generation 1 Discord bot that recreates the authentic Gen 1 experience with modern Discord integration.

## Features

- **Pokemon Spawning**: Random Pokemon spawn in configured channels based on message activity
- **Enhanced Catching System**: Improved catch rates with different Pokeballs
- **Trainer Progression**: Start your journey, build your party, manage your PC box
- **Authentic Gen 1 Data**: All 151 original Pokemon with accurate stats and types
- **Advanced Battle System**: Full turn-based battles with comprehensive status moves and effects
- **Automatic Move Learning**: Pokemon learn moves as they level up with user choice for replacements
- **Gym Challenges**: Battle all 8 Gym Leaders and Elite Four
- **Trading System**: Trade Pokemon with other trainers (includes evolution triggers)
- **Economy System**: Earn money, buy items, and manage inventory
- **Complete Moveset**: All Gen 1 moves including TMs and HMs with proper level-up movesets
- **Detailed IV System**: View exact Individual Values (0-15) for all stats
- **Timeout Management**: Battle and trade requests expire with notifications

## Prerequisites

### 1. Python 3.8+
Download and install Python from [python.org](https://www.python.org/downloads/)

### 2. PostgreSQL Database
1. **Install PostgreSQL**:
   - Windows: Download from [postgresql.org](https://www.postgresql.org/download/windows/)
   - macOS: `brew install postgresql`
   - Linux: `sudo apt-get install postgresql postgresql-contrib`

2. **Start PostgreSQL Service**:
   - Windows: Use Services app or `net start postgresql-x64-14`
   - macOS/Linux: `sudo service postgresql start`

3. **Create Database**:
   ```bash
   # Access PostgreSQL as superuser
   sudo -u postgres psql

   # Create database and user
   CREATE DATABASE pokebot;
   CREATE USER pokebotuser WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE pokebot TO pokebotuser;
   \q
   ```

### 3. Discord Bot Setup
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the bot token (keep this secure!)
5. **Bot Settings**:
   - Enable "Message Content Intent" under Privileged Gateway Intents
   - Enable "Server Members Intent" (optional, for user management)
   - Enable "Presence Intent" (optional)
6. **OAuth2 Settings**:
   - Go to OAuth2 → URL Generator
   - **Scopes**: Select `bot` and `applications.commands`
   - **Bot Permissions**: Select:
     - `Administrator` (recommended for full functionality)
     - OR manually select: `Send Messages`, `Use Slash Commands`, `Embed Links`, `Attach Files`, `Read Message History`, `Add Reactions`, `Manage Messages`
7. Copy the generated URL and invite the bot to your server
8. Ensure the bot has Administrator permissions in your server settings

## Installation

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd pokebot
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   ```bash
   # Copy example environment file
   cp .env.example .env

   # Edit .env file with your settings
   DISCORD_TOKEN=your_discord_bot_token
   DATABASE_URL=postgresql://pokebotuser:your_password@localhost/pokebot
   ADMIN_USER_ID=your_discord_user_id
   ```

4. **Database Setup**
   ```bash
   # Run database schema
   psql -d pokebot -U pokebotuser -f database/schema.sql

   # Initialize Pokemon data
   psql -d pokebot -U pokebotuser -f database/init_data.sql
   psql -d pokebot -U pokebotuser -f database/complete_species.sql
   ```

5. **Run the Bot**
   ```bash
   python bot.py
   ```

## Commands

### Getting Started
- `/start` - Begin your Pokemon journey and choose a starter Pokemon
- `/help [category]` - Show bot commands and help information

### Pokemon Management
- `/party` - Display your current party Pokemon
- `/pokebox [page]` - Browse Pokemon stored in your PC
- `/stats [position]` - View detailed stats, exact IVs, and moves of a party Pokemon (position 1-6)
- `/choosemove` - Choose which move to replace when learning a new move
- `/forgetmove` - Skip learning a new move when Pokemon already knows 4 moves
- `/deposit [position]` - Move Pokemon from party to PC (position 1-6)
- `/withdraw [pokemon_id]` - Move Pokemon from PC to party
- `/switch [position1] [position2]` - Reorder Pokemon in your party

### Catching & Spawning
- `/catch [pokeball_type]` - Attempt to catch spawned Pokemon
- `/setspawn #channel1 #channel2` - Configure spawn channels (Admin only)
- `/defaultpokeball [ball_type]` - Set your default Pokeball for catching

### Battle System
- `/battle @user` - Challenge another trainer to battle
- `/gym [leader_name]` - Challenge gym leaders (brock, misty, surge, erika, koga, sabrina, blaine, giovanni)
- `/elite4 [member_name]` - Challenge Elite Four (lorelei, bruno, agatha, lance)
- `/champion` - Challenge the Pokemon Champion

### Trading
- `/trade @user [pokemon_id]` - Offer a Pokemon trade to another user
- `/trades` - View your active trade requests
- Trade evolutions automatically trigger (Kadabra→Alakazam, etc.)

### Economy & Items
- `/shop` - View available items for purchase
- `/buy [item] [quantity]` - Purchase items from the shop
- `/inventory` - View your current items
- `/use [item] [pokemon_id]` - Use items on your Pokemon

### Moves & Training
- `/teach [pokemon_id] [tm/hm]` - Teach TM or HM moves to Pokemon
- `/moves [pokemon_id]` - View a Pokemon's current moveset (deprecated, use /stats)

### Information & Progress
- `/trainerstats [@user]` - View detailed trainer statistics and progress
- `/pokedex [page]` - Check your Pokedex progress (caught/seen Pokemon)
- `/leaderboard [category]` - View server leaderboards (money, badges, pokemon)

### Admin Commands (Admin Only)
- `/spawn [pokemon] [level] [shiny]` - Force spawn a specific Pokemon
- `/givemoney @user [amount]` - Give money to a user
- `/giveitem @user [item] [quantity]` - Give items to a user
- `/resetuser @user` - Reset a user's progress completely
- `/setlevel @user [pokemon_id] [level]` - Set a Pokemon's level

## Game Features

### Pokemon Spawning System
- Pokemon spawn randomly in configured channels based on message activity
- Spawn rates: 10-20 messages trigger a spawn
- Rarity system with improved catch rates:
  - Common: 85% base catch rate
  - Uncommon: 65% base catch rate
  - Rare: 45% base catch rate
  - Legendary: 15% base catch rate
- 1/4096 chance for shiny Pokemon

### Enhanced Pokeball System & Catch Rates
- **Pokeball**: 1.2x multiplier (improved basic catch rate)
- **Great Ball**: 1.8x multiplier (significantly better catch rate)
- **Ultra Ball**: 2.5x multiplier (very high catch rate)
- **Master Ball**: 100% catch rate (never fails)

### Automatic Move Learning System
- Pokemon automatically learn moves as they level up based on authentic Gen 1 movesets
- If Pokemon knows fewer than 4 moves, new moves are learned automatically
- If Pokemon knows 4 moves, player must choose which move to replace or skip learning
- Players cannot battle or trade while having pending move learning decisions
- Use `/choosemove` to select which move to replace or `/forgetmove` to skip learning

### Advanced Battle System
- Turn-based combat with authentic Gen 1 mechanics
- Complete type effectiveness system (18 types with proper interactions)
- Comprehensive stat stage modifications (-6 to +6) for all stats
- Full status effect system (poison, burn, paralysis, sleep, freeze, confusion)
- 40+ status moves implemented including Transform, Leech Seed, and stat boosters
- Critical hit system (6.25% base, 12.5% for high-crit moves)
- Accuracy and evasion calculations with stat modifications
- Secondary effects on attacking moves (paralysis, burn, poison chances)
- Real-time battle UI with status indicators and stat changes
- 3-minute turn timeout with auto-forfeit and button disabling
- Battle request expiration with notifications

### Gym Challenge System
- 8 Gym Leaders with progressive difficulty
- Elite Four battles with type specialists
- Champion battle with diverse team
- Badge progression system
- Substantial monetary rewards for victories

### Economy System
- Earn money through battles and daily activities
- Shop system with Pokeballs, potions, and TMs/HMs
- TM prices: 3,000-7,500 rupees
- HM prices: 10,000 rupees (reusable)
- Item usage system for healing and stat boosts

### Enhanced Trading System
- Secure Pokemon trading between users with pending move learning checks
- Trade evolution triggers (Kadabra→Alakazam, Machoke→Machamp, Haunter→Gengar, Graveler→Golem)
- Trade request system with 5-minute expiration and notifications
- Cannot trade while having pending move learning decisions

### Complete Gen 1 Experience
- All 151 original Pokemon with accurate base stats and proper gender forms (Nidoran♀/♂)
- Complete moveset with 165+ moves and authentic level-up movesets
- All 50 TMs and 5 HMs available for purchase and teaching
- Automatic move learning system based on authentic Gen 1 data
- Detailed IV system showing exact values (0-15) instead of descriptions
- Authentic type chart and comprehensive battle mechanics
- Proper status move implementations including Transform and stat modifications

## Database Schema

The bot uses PostgreSQL with these main tables:
- `users` - Trainer information and progress
- `pokemon` - Individual Pokemon instances with stats and moves
- `pokemon_species` - Base Pokemon data (stats, types, movesets)
- `user_inventory` - Item storage and quantities
- `server_config` - Server-specific settings (spawn channels)
- `battles` - Battle history and active battle data

## Configuration

### Environment Variables (.env)
```
DISCORD_TOKEN=your_discord_bot_token
DATABASE_URL=postgresql://username:password@localhost/pokebot
ADMIN_USER_ID=your_discord_user_id_for_admin_commands
```

### Server Setup
1. Use `/setspawn #channel1 #channel2` to configure where Pokemon spawn
2. Pokemon will spawn based on message activity in these channels
3. Users can catch Pokemon using `/catch` command
4. Set up roles/permissions as needed for your server

## New Features in Latest Update

**Automatic Move Learning:**
- Pokemon learn moves automatically as they level up
- Interactive choice system when Pokemon already knows 4 moves
- Cannot battle or trade with pending move decisions

**Enhanced Battle System:**
- 40+ status moves implemented with real effects
- Transform mechanic copies opponent's stats and moves
- Comprehensive stat modifications and status conditions
- Real-time battle UI with status indicators

**Improved Catch Rates:**
- All Pokeball types have increased effectiveness
- Better success rates across all rarity tiers

**Detailed IV Display:**
- Exact IV numbers (0-15) shown instead of descriptions
- Clear stat breakdown for competitive analysis

**Timeout Management:**
- Battle and trade requests expire with notifications
- Buttons disable when timeouts occur
- Clear feedback when requests expire

## Troubleshooting

### Common Issues

**Bot won't start:**
- Check Discord token is correct in .env file
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify PostgreSQL is running and accessible
- Ensure `levelup_moves.json` file is in the root directory

**Database connection errors:**
- Check DATABASE_URL format in .env file
- Ensure PostgreSQL service is running
- Verify database and user exist with proper permissions

**Pokemon not spawning:**
- Use `/setspawn` command to configure spawn channels
- Check that Professor Byte has permissions to send messages in spawn channels
- Ensure message activity is happening in configured channels

**Commands not working:**
- Verify Professor Byte has Administrator permissions in your server
- Check that slash commands are synced (restart bot if needed)
- Ensure users have started their journey with `/start`

**Move learning issues:**
- If stuck with pending moves, use `/choosemove` or `/forgetmove`
- Cannot battle or trade until move learning decisions are made
- Check that `levelup_moves.json` is properly formatted

**Battle/Trade timeouts:**
- Battle requests expire after 1 minute
- Trade requests expire after 5 minutes
- Battle turns timeout after 3 minutes with auto-forfeit

### File Requirements
Ensure these files are present in your bot directory:
- `levelup_moves.json` - Contains move learning data for all Pokemon
- All files from the repository including the new `cogs/move_learning.py`

### Support
For additional help or bug reports, check Professor Byte's error logs and ensure all setup steps were completed correctly. The bot now includes comprehensive move learning, enhanced battle mechanics, and improved user experience features.