import json
from scraper import get_moves_for_pokemon
import sys

def build_pokemon_moves_json():
    """
    Reads a list of Pokémon names from pokemon_list.txt, scrapes the
    level-up moves for each, and saves the collected data to
    pokemon_moves.json.
    """
    try:
        with open("pokemon_list.txt", "r") as f:
            pokemon_list = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Error: pokemon_list.txt not found.")
        return

    all_pokemon_moves = {}
    total_pokemon = len(pokemon_list)

    print(f"Starting to fetch moves for {total_pokemon} Pokémon...")

    for i, pokemon_name in enumerate(pokemon_list, 1):
        print(f"({i}/{total_pokemon}) Fetching moves for {pokemon_name}...")

        moves = get_moves_for_pokemon(pokemon_name)

        if moves:
            all_pokemon_moves[pokemon_name] = moves
            print(f"    ...Success, found {len(moves)} move levels.")
        else:
            print(f"    ...Warning: No moves found for {pokemon_name}. It might be a Pokémon with no level-up moves (e.g., Kakuna) or there was a parsing issue.")
            # Still add it to the JSON, but with an empty move set
            all_pokemon_moves[pokemon_name] = {}

    output_filename = "pokemon_moves.json"
    try:
        with open(output_filename, "w") as f:
            json.dump(all_pokemon_moves, f, indent=4)
        print(f"\nSuccessfully created {output_filename} with data for {len(all_pokemon_moves)} Pokémon.")
    except IOError as e:
        print(f"\nError writing to {output_filename}: {e}")

if __name__ == '__main__':
    build_pokemon_moves_json()
