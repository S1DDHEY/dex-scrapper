import requests
import json
import os
import time
import schedule
from dotenv import load_dotenv

load_dotenv()

BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")

# Files to store processed pairs, no-data pairs, and coins with socials
PROCESSED_PAIRS_FILE = "./test_coin_data/processed_pairs.json"
NO_DATA_PAIRS_FILE = "./test_coin_data/no_data_pairs.json"
COINS_WITH_SOCIALS_FILE = "./test_coin_data/coins_with_socials.json"

# Load processed pairs
if os.path.exists(PROCESSED_PAIRS_FILE):
    with open(PROCESSED_PAIRS_FILE, "r") as file:
        try:
            processed_pairs = set(json.load(file))
        except json.JSONDecodeError:
            processed_pairs = set()
else:
    processed_pairs = set()

# Load no-data pairs
if os.path.exists(NO_DATA_PAIRS_FILE):
    with open(NO_DATA_PAIRS_FILE, "r") as file:
        try:
            no_data_pairs = set(json.load(file))
        except json.JSONDecodeError:
            no_data_pairs = set()
else:
    no_data_pairs = set()

# Load coins with socials
if os.path.exists(COINS_WITH_SOCIALS_FILE):
    with open(COINS_WITH_SOCIALS_FILE, "r") as file:
        try:
            coins_with_socials = set(json.load(file))
        except json.JSONDecodeError:
            coins_with_socials = set()
else:
    coins_with_socials = set()

def save_processed_pairs():
    """Save processed pairs to a file."""
    with open(PROCESSED_PAIRS_FILE, "w") as file:
        json.dump(list(processed_pairs), file, indent=4)

def save_no_data_pairs():
    """Save no-data pairs to a file."""
    with open(NO_DATA_PAIRS_FILE, "w") as file:
        json.dump(list(no_data_pairs), file, indent=4)

def save_coins_with_socials():
    """Save coins with socials to a file."""
    with open(COINS_WITH_SOCIALS_FILE, "w") as file:
        json.dump(list(coins_with_socials), file, indent=4)

def fetch_pair_data(pair_address):
    """
    Fetch data for a given pair from Dex Screener API.
    
    Returns:
        "no_data"    : if no data is returned (coin remains in no_data_pairs).
        "no_socials" : if data is returned but no socials are found (coin will be removed permanently).
        "success"    : if data with socials is returned.
    """
    url = f"https://api.dexscreener.com/latest/dex/search?q={pair_address}"
    json_file = f"./test_coin_data/{pair_address}.json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Check if any data was returned
        if 'pairs' not in data or not data['pairs']:
            print(f"No data found for {pair_address}")
            no_data_pairs.add(pair_address)
            save_no_data_pairs()
            return "no_data"
        
        # Data is returned; now check for socials
        pair = data['pairs'][0]
        socials = pair.get("info", {}).get("socials", [])
        
        if not socials:
            print(f"Skipping {pair_address}, no socials found.")
            # Remove coin from no_data_pairs (if present) so it isn't retried further.
            if pair_address in no_data_pairs:
                no_data_pairs.remove(pair_address)
                save_no_data_pairs()
            return "no_socials"
        
        # Data with socials is available:
        if pair_address in no_data_pairs:
            no_data_pairs.remove(pair_address)
            save_no_data_pairs()
        
        processed_pairs.add(pair_address)
        coins_with_socials.add(pair_address)
        save_processed_pairs()
        save_coins_with_socials()

        with open(json_file, 'w') as file:
            json.dump(data, file, indent=4)
        
        print(f"New coin with socials found! Data saved to {json_file}.")
        return "success"
    except requests.exceptions.RequestException as e:
        print(f"API request failed for {pair_address}:", e)
        return "no_data"  # On failure, treat it as no data for now.

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
        
        for item in items:
            pair_address = item.get("address")
            if not pair_address or pair_address in processed_pairs or pair_address in no_data_pairs:
                continue
            
            # We process only if fetch_pair_data returns "success"
            status = fetch_pair_data(pair_address)
            if status == "success":
                # Already saved and updated processed lists in fetch_pair_data
                pass
    
    except requests.exceptions.RequestException as e:
        print("API request for new pairs failed:", e)
    except Exception as e:
        print("An error occurred while fetching new pairs:", e)

def retry_no_data_pairs():
    """
    Retry fetching data for pairs previously marked as having no data.
    Remove a coin from no_data_pairs only if:
      - It now returns data with socials ("success") OR 
      - It returns data but no socials ("no_socials").
    If it still returns "no_data", keep it in no_data_pairs for future retries.
    """
    print("Retrying no data pairs...")
    to_remove = set()
    
    for pair_address in list(no_data_pairs):
        status = fetch_pair_data(pair_address)
        if status in ("success", "no_socials"):
            print(f"Removing {pair_address} from no_data_pairs permanently.")
            to_remove.add(pair_address)
        else:
            # Status is "no_data": leave it for future retries.
            print(f"{pair_address} still has no data; will retry later.")
    
    if to_remove:
        no_data_pairs.difference_update(to_remove)
        save_no_data_pairs()

# Schedule tasks
schedule.every(5).seconds.do(fetch_new_pairs)
schedule.every(5).seconds.do(retry_no_data_pairs)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
