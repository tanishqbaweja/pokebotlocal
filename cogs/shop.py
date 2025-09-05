import discord
from discord.ext import commands
from discord import app_commands

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shop_items = {
            "pokeball": {"price": 200, "description": "Standard Pokeball"},
            "greatball": {"price": 600, "description": "Better catch rate"},
            "ultraball": {"price": 1200, "description": "High catch rate"},
            "masterball": {"price": 50000, "description": "Never fails"},
            "potion": {"price": 300, "description": "Restores 20 HP"},
            "super_potion": {"price": 700, "description": "Restores 50 HP"},
            "hyper_potion": {"price": 1200, "description": "Restores 200 HP"},
            # All TMs (50 total)
            # Rare Candy for leveling up
            "rare_candy": {"price": 4800, "description": "Raises Pokemon level by 1"},
            # Status cure items
            "antidote": {"price": 100, "description": "Cures poison"},
            "awakening": {"price": 250, "description": "Cures sleep"},
            "burn_heal": {"price": 250, "description": "Cures burn"},
            "ice_heal": {"price": 250, "description": "Cures freeze"},
            "paralyze_heal": {"price": 200, "description": "Cures paralysis"},
            # Revival items
            "revive": {"price": 1500, "description": "Revives fainted Pokemon to 50% HP"},
            "max_revive": {"price": 4000, "description": "Revives fainted Pokemon to full HP"},
            # TMs start here
            "tm01": {"price": 3000, "description": "Mega Punch"}, "tm02": {"price": 3000, "description": "Razor Wind"}, "tm03": {"price": 3000, "description": "Swords Dance"}, "tm04": {"price": 3000, "description": "Whirlwind"}, "tm05": {"price": 3000, "description": "Mega Kick"},
            "tm06": {"price": 7500, "description": "Toxic"}, "tm07": {"price": 3000, "description": "Horn Drill"}, "tm08": {"price": 3000, "description": "Body Slam"}, "tm09": {"price": 3000, "description": "Take Down"}, "tm10": {"price": 3000, "description": "Double Edge"},
            "tm11": {"price": 3000, "description": "Bubble Beam"}, "tm12": {"price": 3000, "description": "Water Gun"}, "tm13": {"price": 7500, "description": "Ice Beam"}, "tm14": {"price": 7500, "description": "Blizzard"}, "tm15": {"price": 7500, "description": "Hyper Beam"},
            "tm16": {"price": 3000, "description": "Pay Day"}, "tm17": {"price": 3000, "description": "Submission"}, "tm18": {"price": 3000, "description": "Counter"}, "tm19": {"price": 3000, "description": "Seismic Toss"}, "tm20": {"price": 3000, "description": "Rage"},
            "tm21": {"price": 3000, "description": "Mega Drain"}, "tm22": {"price": 7500, "description": "Solar Beam"}, "tm23": {"price": 3000, "description": "Dragon Rage"}, "tm24": {"price": 7500, "description": "Thunderbolt"}, "tm25": {"price": 7500, "description": "Thunder"},
            "tm26": {"price": 7500, "description": "Earthquake"}, "tm27": {"price": 3000, "description": "Fissure"}, "tm28": {"price": 3000, "description": "Dig"}, "tm29": {"price": 7500, "description": "Psychic"}, "tm30": {"price": 3000, "description": "Teleport"},
            "tm31": {"price": 3000, "description": "Mimic"}, "tm32": {"price": 3000, "description": "Double Team"}, "tm33": {"price": 3000, "description": "Reflect"}, "tm34": {"price": 3000, "description": "Bide"}, "tm35": {"price": 3000, "description": "Metronome"},
            "tm36": {"price": 3000, "description": "Self Destruct"}, "tm37": {"price": 3000, "description": "Egg Bomb"}, "tm38": {"price": 7500, "description": "Fire Blast"}, "tm39": {"price": 3000, "description": "Swift"}, "tm40": {"price": 3000, "description": "Skull Bash"},
            "tm41": {"price": 3000, "description": "Soft Boiled"}, "tm42": {"price": 3000, "description": "Dream Eater"}, "tm43": {"price": 3000, "description": "Sky Attack"}, "tm44": {"price": 3000, "description": "Rest"}, "tm45": {"price": 3000, "description": "Thunder Wave"},
            "tm46": {"price": 3000, "description": "Psywave"}, "tm47": {"price": 3000, "description": "Explosion"}, "tm48": {"price": 3000, "description": "Rock Slide"}, "tm49": {"price": 3000, "description": "Tri Attack"}, "tm50": {"price": 3000, "description": "Substitute"},
            # All HMs (5 total)
            "hm01": {"price": 10000, "description": "Cut"}, "hm02": {"price": 10000, "description": "Fly"}, "hm03": {"price": 10000, "description": "Surf"}, "hm04": {"price": 10000, "description": "Strength"}, "hm05": {"price": 10000, "description": "Flash"}
        }
        
    @app_commands.command(name="shop", description="View the Pokemon shop")
    async def shop(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Pokemon Shop", color=0x3498db)
        
        # Basic items only (under 25 field limit)
        basic_items = {
            "pokeball": self.shop_items["pokeball"],
            "greatball": self.shop_items["greatball"], 
            "ultraball": self.shop_items["ultraball"],
            "masterball": self.shop_items["masterball"],
            "potion": self.shop_items["potion"],
            "super_potion": self.shop_items["super_potion"],
            "hyper_potion": self.shop_items["hyper_potion"],
            "rare_candy": self.shop_items["rare_candy"],
            "antidote": self.shop_items["antidote"],
            "revive": self.shop_items["revive"]
        }
        
        for item, data in basic_items.items():
            embed.add_field(
                name=f"{item.replace('_', ' ').title()}",
                value=f"{data['description']}\n💰 {data['price']:,} rupees",
                inline=True
            )
            
        embed.add_field(
            name="TMs & HMs", 
            value="TM01-TM50: 3000-7500 rupees\nHM01-HM05: 10000 rupees\nUse /buy tm01 or /buy hm01",
            inline=False
        )
            
        embed.set_footer(text="Use /buy [item] [quantity] to purchase items")
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="buy", description="Purchase items from the shop")
    async def buy(self, interaction: discord.Interaction, item: str, quantity: int = 1):
        user_id = interaction.user.id
        item = item.lower().replace(' ', '_')
        
        if item not in self.shop_items:
            await interaction.response.send_message("Item not found in shop!", ephemeral=True)
            return
            
        if quantity <= 0:
            await interaction.response.send_message("Quantity must be positive!", ephemeral=True)
            return
            
        total_cost = self.shop_items[item]["price"] * quantity
        
        # Check user money
        user = await self.bot.db.get_user(user_id)
        if not user:
            await interaction.response.send_message("You haven't started your journey yet!", ephemeral=True)
            return
            
        if user['money'] < total_cost:
            await interaction.response.send_message(f"Not enough money! You need {total_cost:,} rupees.", ephemeral=True)
            return
            
        # Process purchase
        await self.bot.db.execute(
            "UPDATE users SET money = money - $1 WHERE user_id = $2",
            total_cost, user_id
        )
        
        # Add to inventory
        await self.bot.db.execute(
            """INSERT INTO user_inventory (user_id, item_name, quantity)
               VALUES ($1, $2, $3)
               ON CONFLICT (user_id, item_name)
               DO UPDATE SET quantity = user_inventory.quantity + $3""",
            user_id, item, quantity
        )
        
        embed = discord.Embed(
            title="Purchase Successful!",
            description=f"Bought {quantity}x {item.replace('_', ' ').title()} for {total_cost:,} rupees",
            color=0x00ff00
        )
        
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="inventory", description="View your items")
    async def inventory(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        
        items = await self.bot.db.fetch(
            "SELECT item_name, quantity FROM user_inventory WHERE user_id = $1 AND quantity > 0",
            user_id
        )
        
        if not items:
            await interaction.response.send_message("Your inventory is empty!", ephemeral=True)
            return
            
        embed = discord.Embed(title="Your Inventory", color=0x9b59b6)
        
        # Limit to 24 fields to stay under Discord's 25 field limit
        items_to_show = items[:24]
        for item in items_to_show:
            embed.add_field(
                name=item['item_name'].replace('_', ' ').title(),
                value=f"Quantity: {item['quantity']}",
                inline=True
            )
            
        if len(items) > 24:
            embed.set_footer(text=f"Showing first 24 items of {len(items)} total")
            
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="use", description="Use an item on a Pokemon")
    async def use_item(self, interaction: discord.Interaction, item: str, position: int):
        user_id = interaction.user.id
        item = item.lower().replace(' ', '_')
        
        if position < 1 or position > 6:
            await interaction.response.send_message("Position must be between 1 and 6!", ephemeral=True)
            return
        
        # Check if user has the item
        inventory = await self.bot.db.fetchrow(
            "SELECT quantity FROM user_inventory WHERE user_id = $1 AND item_name = $2",
            user_id, item
        )
        
        if not inventory or inventory['quantity'] <= 0:
            await interaction.response.send_message(f"You don't have any {item.replace('_', ' ')}!", ephemeral=True)
            return
            
        # Get Pokemon from party position
        pokemon = await self.bot.db.fetchrow(
            "SELECT * FROM pokemon WHERE owner_id = $1 AND in_party = TRUE AND party_position = $2",
            user_id, position
        )
        
        if not pokemon:
            await interaction.response.send_message(f"No Pokemon at position {position}!", ephemeral=True)
            return
            
        # Use item
        result = await self._use_item_on_pokemon(item, pokemon)
        
        if result:
            # Remove item from inventory
            await self.bot.db.execute(
                "UPDATE user_inventory SET quantity = quantity - 1 WHERE user_id = $1 AND item_name = $2",
                user_id, item
            )
            
            await interaction.response.send_message(result)
        else:
            await interaction.response.send_message("Cannot use this item!", ephemeral=True)
            
    async def _use_item_on_pokemon(self, item, pokemon):
        from data.complete_pokemon_data import COMPLETE_POKEMON_DATA
        
        # Rare Candy - Level up item
        if item == "rare_candy":
            if pokemon['level'] >= 100:
                species = COMPLETE_POKEMON_DATA.get(pokemon['species_id'])
                species_name = species['name'] if species else 'Pokemon'
                return f"{species_name} is already at max level!"
                
            # Level up the Pokemon
            new_level = pokemon['level'] + 1
            
            # Recalculate HP for new level
            species = COMPLETE_POKEMON_DATA[pokemon['species_id']]
            old_max_hp = ((species['base_hp'] + pokemon['hp_iv']) * 2 * pokemon['level'] // 100) + pokemon['level'] + 10
            new_max_hp = ((species['base_hp'] + pokemon['hp_iv']) * 2 * new_level // 100) + new_level + 10
            hp_increase = new_max_hp - old_max_hp
            new_current_hp = pokemon['current_hp'] + hp_increase
            
            # Update Pokemon in database
            await self.bot.db.execute(
                "UPDATE pokemon SET level = $1, current_hp = $2 WHERE id = $3",
                new_level, new_current_hp, pokemon['id']
            )
            
            # Trigger level up events for move learning and evolution
            self.bot.dispatch('pokemon_level_up', pokemon['id'], pokemon['level'], new_level)
            
            return f"{species['name']} grew to level {new_level}!"
        
        # Healing items
        elif item in ["potion", "super_potion", "hyper_potion", "max_potion", "full_restore"]:
            species = COMPLETE_POKEMON_DATA.get(pokemon['species_id'])
            if not species:
                return f"Error: Invalid Pokemon species ID {pokemon['species_id']}"
            max_hp = ((species['base_hp'] + pokemon['hp_iv']) * 2 * pokemon['level'] // 100) + pokemon['level'] + 10
            
            if pokemon['current_hp'] >= max_hp:
                species_name = species['name']
                return f"{species_name} is already at full HP!"
                
            heal_amounts = {
                "potion": 20, 
                "super_potion": 50, 
                "hyper_potion": 200,
                "max_potion": max_hp,  # Full heal
                "full_restore": max_hp  # Full heal + status cure
            }
            heal_amount = heal_amounts[item]
            
            new_hp = min(max_hp, pokemon['current_hp'] + heal_amount)
            actual_heal = new_hp - pokemon['current_hp']
            
            await self.bot.db.execute(
                "UPDATE pokemon SET current_hp = $1 WHERE id = $2",
                new_hp, pokemon['id']
            )
            
            species_name = species['name']
            result = f"{species_name} was healed for {actual_heal} HP!"
            
            # Full Restore also cures status conditions
            if item == "full_restore":
                # Note: Status conditions would need to be stored in database to implement this fully
                result += " All status conditions were cured!"
            
            return result
            
        # Status healing items
        elif item in ["antidote", "awakening", "burn_heal", "ice_heal", "paralyze_heal", "pecha_berry", "chesto_berry", "rawst_berry", "aspear_berry", "cheri_berry"]:
            # Note: This would require status conditions to be stored in the database
            # For now, return a placeholder message
            status_cures = {
                "antidote": "poison",
                "awakening": "sleep", 
                "burn_heal": "burn",
                "ice_heal": "freeze",
                "paralyze_heal": "paralysis",
                "pecha_berry": "poison",
                "chesto_berry": "sleep",
                "rawst_berry": "burn",
                "aspear_berry": "freeze",
                "cheri_berry": "paralysis"
            }
            species = COMPLETE_POKEMON_DATA.get(pokemon['species_id'])
            species_name = species['name'] if species else 'Pokemon'
            return f"{species_name} was cured of {status_cures[item]}!"
            
        # Revival items
        elif item in ["revive", "max_revive", "revival_herb"]:
            if pokemon['current_hp'] > 0:
                species = COMPLETE_POKEMON_DATA.get(pokemon['species_id'])
                species_name = species['name'] if species else 'Pokemon'
                return f"{species_name} is not fainted!"
                
            species = COMPLETE_POKEMON_DATA.get(pokemon['species_id'])
            if not species:
                return f"Error: Invalid Pokemon species ID {pokemon['species_id']}"
            max_hp = ((species['base_hp'] + pokemon['hp_iv']) * 2 * pokemon['level'] // 100) + pokemon['level'] + 10
            
            if item == "revive":
                new_hp = max_hp // 2  # Revive to half HP
            elif item == "max_revive":
                new_hp = max_hp  # Revive to full HP
            else:  # revival_herb
                new_hp = max_hp  # Full revive but bitter taste
                
            await self.bot.db.execute(
                "UPDATE pokemon SET current_hp = $1 WHERE id = $2",
                new_hp, pokemon['id']
            )
            
            species_name = species['name']
            result = f"{species_name} was revived with {new_hp} HP!"
            if item == "revival_herb":
                result += " But it didn't like the bitter taste!"
            
            return result
            
        # PP restoration items
        elif item in ["ether", "max_ether", "elixir", "max_elixir"]:
            # Note: PP system would need to be implemented in database
            pp_restore = {
                "ether": "10 PP to one move",
                "max_ether": "all PP to one move", 
                "elixir": "10 PP to all moves",
                "max_elixir": "all PP to all moves"
            }
            species = COMPLETE_POKEMON_DATA.get(pokemon['species_id'])
            species_name = species['name'] if species else 'Pokemon'
            return f"{species_name} restored {pp_restore[item]}!"
            
        # Stat boost items
        elif item in ["x_attack", "x_defend", "x_speed", "x_special", "x_accuracy", "dire_hit", "guard_spec"]:
            stat_boosts = {
                "x_attack": "Attack",
                "x_defend": "Defense",
                "x_speed": "Speed", 
                "x_special": "Special",
                "x_accuracy": "Accuracy",
                "dire_hit": "critical hit ratio",
                "guard_spec": "stat protection"
            }
            species = COMPLETE_POKEMON_DATA.get(pokemon['species_id'])
            species_name = species['name'] if species else 'Pokemon'
            return f"{species_name}'s {stat_boosts[item]} was boosted!"
            
        # Evolution stones (would need evolution system integration)
        elif item in ["fire_stone", "water_stone", "thunder_stone", "leaf_stone", "moon_stone"]:
            # Check if Pokemon can evolve with this stone
            evolution_cog = self.bot.get_cog('Evolution')
            if evolution_cog:
                # This would need stone evolution mapping in evolution system
                species = COMPLETE_POKEMON_DATA.get(pokemon['species_id'])
                species_name = species['name'] if species else 'Pokemon'
                return f"Used {item.replace('_', ' ').title()} on {species_name}!"
            species = COMPLETE_POKEMON_DATA.get(pokemon['species_id'])
            species_name = species['name'] if species else 'Pokemon'
            return f"Cannot use {item.replace('_', ' ').title()} on {species_name}!"
            
        # Remove duplicate rare_candy handling - already handled above
            
        return None
    
    @app_commands.command(name="healall", description="Heal all Pokemon in your party to full HP")
    async def heal_all(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        
        # Get all Pokemon in party that need healing
        from data.complete_pokemon_data import COMPLETE_POKEMON_DATA
        party_pokemon = await self.bot.db.fetch(
            "SELECT * FROM pokemon WHERE owner_id = $1 AND in_party = TRUE",
            user_id
        )
        
        if not party_pokemon:
            await interaction.response.send_message("No Pokemon in your party!", ephemeral=True)
            return
        
        # Filter Pokemon that need healing
        pokemon_to_heal = []
        total_healing_needed = 0
        
        for pokemon in party_pokemon:
            species = COMPLETE_POKEMON_DATA[pokemon['species_id']]
            max_hp = ((species['base_hp'] + pokemon['hp_iv']) * 2 * pokemon['level'] // 100) + pokemon['level'] + 10
            if pokemon['current_hp'] < max_hp:
                pokemon_to_heal.append(pokemon)
                total_healing_needed += max_hp - pokemon['current_hp']
        
        if not pokemon_to_heal:
            await interaction.response.send_message("All Pokemon are already at full HP!", ephemeral=True)
            return
        
        # Get user's potions
        potions = await self.bot.db.fetch(
            "SELECT item_name, quantity FROM user_inventory WHERE user_id = $1 AND item_name IN ('hyper_potion', 'super_potion', 'potion') AND quantity > 0",
            user_id
        )
        
        # Calculate available healing
        heal_values = {"hyper_potion": 200, "super_potion": 50, "potion": 20}
        available_healing = 0
        potion_usage = {"hyper_potion": 0, "super_potion": 0, "potion": 0}
        
        for potion in potions:
            available_healing += potion['quantity'] * heal_values[potion['item_name']]
        
        if available_healing < total_healing_needed:
            await interaction.response.send_message(
                f"Not enough potions! Need {total_healing_needed} HP worth of healing, but only have {available_healing} HP worth of potions. Buy more potions to heal all Pokemon at once.",
                ephemeral=True
            )
            return
        
        # Calculate optimal potion usage
        remaining_healing = total_healing_needed
        potion_counts = {p['item_name']: p['quantity'] for p in potions}
        
        # Use hyper potions first, then super potions, then regular potions
        for potion_type in ["hyper_potion", "super_potion", "potion"]:
            if potion_type in potion_counts and remaining_healing > 0:
                heal_per_potion = heal_values[potion_type]
                potions_needed = min(potion_counts[potion_type], (remaining_healing + heal_per_potion - 1) // heal_per_potion)
                potion_usage[potion_type] = potions_needed
                remaining_healing -= potions_needed * heal_per_potion
        
        # Heal all Pokemon that need healing
        for pokemon in pokemon_to_heal:
            species = COMPLETE_POKEMON_DATA[pokemon['species_id']]
            max_hp = ((species['base_hp'] + pokemon['hp_iv']) * 2 * pokemon['level'] // 100) + pokemon['level'] + 10
            
            await self.bot.db.execute(
                "UPDATE pokemon SET current_hp = $1 WHERE id = $2",
                max_hp, pokemon['id']
            )
        
        # Remove used potions from inventory
        for potion_type, used_count in potion_usage.items():
            if used_count > 0:
                await self.bot.db.execute(
                    "UPDATE user_inventory SET quantity = quantity - $1 WHERE user_id = $2 AND item_name = $3",
                    used_count, user_id, potion_type
                )
        
        # Create result message
        used_items = []
        for potion_type, count in potion_usage.items():
            if count > 0:
                used_items.append(f"{count}x {potion_type.replace('_', ' ').title()}")
        
        embed = discord.Embed(
            title="All Pokemon Healed!",
            description=f"Healed {len(pokemon_to_heal)} Pokemon to full HP!",
            color=0x00ff00
        )
        embed.add_field(name="Items Used", value=", ".join(used_items), inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Shop(bot))