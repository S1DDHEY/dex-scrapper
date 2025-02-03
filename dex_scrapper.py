import requests
import json
import os
import time
import schedule
from dotenv import load_dotenv

load_dotenv()

BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")

# File to store processed pairs
PROCESSED_PAIRS_FILE = "processed_pairs.json"

# Load processed pairs
if os.path.exists(PROCESSED_PAIRS_FILE):
    with open(PROCESSED_PAIRS_FILE, "r") as file:
        try:
            processed_pairs = set(json.load(file))
        except json.JSONDecodeError:
            processed_pairs = set()
else:
    processed_pairs = set()

no_data_pairs = set()

def save_processed_pairs():
    """Save processed pairs to a file."""
    with open(PROCESSED_PAIRS_FILE, "w") as file:
        json.dump(list(processed_pairs), file, indent=4)

def fetch_pair_data(pair_address):
    """Fetch data for a given pair from Dex Screener API."""
    # time.sleep(20)

    if pair_address in no_data_pairs:
        return False  # Skip already marked addresses

    url = f"https://api.dexscreener.com/latest/dex/search?q={pair_address}"
    json_file = f"./coin_data/{pair_address}.json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'pairs' not in data or not data['pairs']:
            print(f"No data found for {pair_address}")
            no_data_pairs.add(pair_address)  # Mark it as "no data"
            return False
        
        # If data is found, remove it from no_data_pairs
        if pair_address in no_data_pairs:
            no_data_pairs.remove(pair_address) 

        with open(json_file, 'w') as file:
            json.dump(data, file, indent=4)
        
        print(f"New coin found! Data saved to {json_file}.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"API request failed for {pair_address}:", e)
        return False

def fetch_new_pairs():
    """Fetch new pairs from BirdEye API and process them."""
    new_pairs_url = "https://public-api.birdeye.so/defi/v2/tokens/new_listing?limit=5&meme_platform_enabled=false"
    headers = {
        "accept": "application/json",
        "x-chain": "solana",
        "X-API-KEY": BIRDEYE_API_KEY
    }
    
    try:
        response = requests.get(new_pairs_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        items = data.get("data", {}).get("items", [])
        
        if not items:
            return
        
        new_pairs_found = False
        
        for item in items:
            pair_address = item.get("address")
            if not pair_address or pair_address in processed_pairs or pair_address in no_data_pairs:
                continue
            
            if fetch_pair_data(pair_address):
                processed_pairs.add(pair_address)
                new_pairs_found = True
        
        if new_pairs_found:
            save_processed_pairs()
    
    except requests.exceptions.RequestException as e:
        print("API request for new pairs failed:", e)
    except Exception as e:
        print("An error occurred while fetching new pairs:", e)

schedule.every(5).seconds.do(fetch_new_pairs)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
