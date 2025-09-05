import requests
from bs4 import BeautifulSoup
import json
import re
import time

def get_moves_for_pokemon(pokemon_name: str):
    """
    Scrapes the Pokémon Database website for the Generation 1 (Yellow version,
    falling back to Red/Blue if Yellow-specific is not available)
    level-up moves for a given Pokémon.

    Args:
        pokemon_name: The name of the Pokémon to look up.

    Returns:
        A dictionary of level-up moves, where keys are levels (str) and
        values are lists of move names (str). Returns an empty dictionary
        if the page cannot be parsed or the Pokémon is not found.
    """
    # Sanitize the Pokémon name for the URL
    if '♀' in pokemon_name:
        url_name = "nidoran-f"
    elif '♂' in pokemon_name:
        url_name = "nidoran-m"
    elif "Farfetch'd" in pokemon_name:
        url_name = "farfetchd"
    elif "Mr. Mime" in pokemon_name:
        url_name = "mr-mime"
    else:
        # General case for names like "Porygon"
        url_name = pokemon_name.lower().replace(" ", "-")

    url = f"https://pokemondb.net/pokedex/{url_name}/moves/1"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        time.sleep(1) # Be polite
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page for {pokemon_name} (url: {url}): {e}")
        return {}

    soup = BeautifulSoup(response.content, "html.parser")
    data_table = None

    # The page uses tabs for different game versions.
    # Yellow is in the panel with id 'tab-moves-2'.
    # If it doesn't exist, the moves are the same as Red/Blue in 'tab-moves-1'.
    yellow_panel = soup.find('div', id='tab-moves-2')
    if yellow_panel:
        data_table = yellow_panel.find('table', class_='data-table')
    else:
        # Fallback to the Red/Blue panel if no specific Yellow panel exists
        rb_panel = soup.find('div', id='tab-moves-1')
        if rb_panel:
            data_table = rb_panel.find('table', class_='data-table')

    if not data_table:
        return {}

    moves = {}
    # Find the 'Moves learnt by level up' table specifically
    level_up_heading = data_table.find_previous('h3', string='Moves learnt by level up')
    if not level_up_heading:
         # Some pages might have h2 instead
         level_up_heading = data_table.find_previous('h2', string='Moves learnt by level up')
         if not level_up_heading:
            return{}

    # Ensure we're looking at the right table associated with the heading
    table_to_parse = level_up_heading.find_next('table', class_='data-table')
    if not table_to_parse:
        return {}

    rows = table_to_parse.find("tbody").find_all("tr")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 2:
            level_str = cols[0].get_text(strip=True)
            move_name_tag = cols[1].find("a", class_="ent-name")

            if level_str and move_name_tag:
                move_name = move_name_tag.get_text(strip=True)
                # Remove non-alphanumeric characters
                move_name_cleaned = re.sub(r'[^A-Za-z0-9]', '', move_name)

                if level_str in moves:
                    if move_name_cleaned not in moves[level_str]:
                        moves[level_str].append(move_name_cleaned)
                else:
                    moves[level_str] = [move_name_cleaned]

    return moves

if __name__ == '__main__':
    # Example usage for testing the script directly
    test_cases = ["Butterfree", "Pikachu", "Mew", "Nidoran♀", "Nidoran♂", "Farfetch'd", "Mr. Mime", "Snorlax"]
    all_results = {}
    for pokemon in test_cases:
        print(f"Fetching moves for {pokemon}...")
        moves = get_moves_for_pokemon(pokemon)
        all_results[pokemon] = moves

    print(json.dumps(all_results, indent=4))
