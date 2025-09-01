# Professor Byte - A Pokémon-themed Discord Bot

Professor Byte is a fully-featured Pokémon Generation 1-style Discord bot that brings the classic monster-catching and battling experience to your server. It features a rich set of commands, a detailed battle system, and a persistent world for you and your friends to explore.

## Core Features

- **Gotta Catch 'Em All!**: Over 150 Pokémon from Generation 1 spawn randomly in your server.
- **Deep Battle System**: Challenge friends to PvP battles with authentic Gen 1 mechanics, including status effects, stat modifiers, and critical hits.
- **Full Progression System**: Battle your way through all 8 Kanto Gym Leaders, defeat the Elite Four, and become the Pokémon League Champion.
- **Robust Economy**: Earn money from battles, buy and sell items at the shop, and manage your inventory.
- **Pokémon Management**: Manage your team of six, store extra Pokémon in the PC, and view detailed stats and IVs for each of your Pokémon.
- **Trading & Evolution**: Trade Pokémon with other trainers. Watch them evolve through leveling up, trading, or using evolution stones.
- **Move Learning**: Pokémon learn new moves as they level up, with an interactive system for choosing which moves to keep. Teach new moves using TMs and HMs.

## Commands

### 🏁 Getting Started
- `/start`: Begin your Pokémon journey!
- `/profile`: View your trainer profile.
- `/party`: View your current party of Pokémon.

### 🐾 Pokémon & Storage
- `/catch [pokeball]`: Catch a wild Pokémon.
- `/pokebox [page]`: View your Pokémon storage.
- `/deposit [position]`: Move a Pokémon from your party to the PC.
- `/withdraw [pokemon_id]`: Move a Pokémon from the PC to your party.
- `/switch [pos1] [pos2]`: Switch the positions of two Pokémon in your party.
- `/stats [position]`: View a Pokémon's stats and moves.

### ✨ Evolution & Moves
- `/evolve [position] [item]`: Use an evolution stone on a Pokémon.
- `/teach [position] [move_item]`: Teach a TM or HM move to a Pokémon.
- `/choosemove`: Choose which move to replace when learning a new one.
- `/forgetmove`: Skip learning a new move.

### ⚔️ Battle & Trading
- `/battle [opponent]`: Challenge another trainer to a battle.
- `/trade [user] [position]`: Offer to trade a Pokémon with another user.

### 🏆 Gyms & The Pokémon League
- `/gym [leader]`: Challenge one of the 8 Kanto Gym Leaders.
- `/elite4 [member]`: Challenge a member of the Elite Four.
- `/champion`: Challenge the Pokémon League Champion.

### 💰 Shop & Items
- `/shop [page]`: View items available for purchase.
- `/buy [item] [quantity]`: Purchase items from the shop.
- `/sell [item] [quantity]`: Sell items to the shop.
- `/inventory [page]`: View your items.
- `/use [item] [position]`: Use a consumable item on a Pokémon.
- `/healall`: Use potions from your inventory to heal your entire party.

### 🔧 Utilities
- `/pokedex [page]`: View your Pokédex completion progress.
- `/defaultpokeball [type]`: Set your default pokéball for `/catch`.
- `/invite`: Get the bot's invite link.
- `/server`: Get the invite link for the official support server.
- `/help`: Show a complete list of bot commands.

### 🔒 Admin Commands
*(Requires Administrator permission)*
- `/setspawn ...`: Configure channels for Pokémon spawns.
- `/spawn ...`: Force a Pokémon to spawn.
- `/givemoney ...`: Give money to a user.
- `/giveitem ...`: Give an item to a user.
- `/resetuser ...`: Reset a user's progress.
- `/setlevel ...`: Set a Pokémon's level.

## Getting Started

1.  **Invite the Bot**: Use the `/invite` command to get the bot's invite link and add it to your server.
2.  **Set Spawn Channels**: A server admin must use the `/setspawn` command to designate at least one channel where Pokémon can appear.
3.  **Begin Your Journey**: Type `/start` to choose your starter Pokémon and begin your adventure!

## Installation (For Self-Hosting)

### Prerequisites
- Python 3.8+
- PostgreSQL Server

### Setup
1.  **Clone the Repository**: `git clone <repository-url>`
2.  **Install Dependencies**: `pip install -r requirements.txt`
3.  **Set Up Environment**: Copy `.env.example` to `.env` and fill in your `DISCORD_TOKEN`, `DATABASE_URL`, and `ADMIN_USER_ID`.
4.  **Database Setup**: Run the `database/schema.sql` file on your PostgreSQL database to set up the required tables.
5.  **Run the Bot**: `python bot.py`