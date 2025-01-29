import requests
import csv
import os
import schedule
import time
from dotenv import load_dotenv

# Directory to store CSV files
output_dir = "./coin_data"
os.makedirs(output_dir, exist_ok=True)

# Single CSV file for all pairs
ALL_PAIRS_CSV = os.path.join(output_dir, "all_pairs.csv")

load_dotenv()

# Keep track of processed pairs
processed_pairs = set()
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")

def fetch_new_pairs():
    # BirdEye API endpoint for new pairs
    new_pairs_url = "https://public-api.birdeye.so/defi/v2/tokens/new_listing?limit=10&meme_platform_enabled=false"
    headers = {
        "accept": "application/json",
        "x-chain": "solana",
        "X-API-KEY": f"{BIRDEYE_API_KEY}"
    }

    try:
        response = requests.get(new_pairs_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        items = data.get("data", {}).get("items", [])

        if not items:
            print("No new pairs found.")
            return

        for item in items:
            pair_address = item.get("address")
            if not pair_address:
                continue

            if pair_address in processed_pairs:
                continue

            if fetch_pair_data(pair_address):
                processed_pairs.add(pair_address)

    except requests.exceptions.RequestException as e:
        print("API request for new pairs failed:", e)
    except Exception as e:
        print("An error occurred while fetching new pairs:", e)

def fetch_pair_data(pair_address):
    # Dex Screener API endpoint for pair data
    url = f"https://api.dexscreener.com/latest/dex/search?q={pair_address}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'pairs' not in data or not data['pairs']:
            return False

        pair = data['pairs'][0]
        socials = pair.get("info", {}).get("socials", [])
        if not socials:
            return False

    except requests.exceptions.RequestException as e:
        print(f"API request failed for pair {pair_address}:", e)
    except KeyError as e:
        print(f"KeyError for pair {pair_address}: {e}")
    except Exception as e:
        print(f"An error occurred for pair {pair_address}: {e}")
    return False

# Schedule the tasks (unchanged)
schedule.every(10).seconds.do(fetch_new_pairs)

while True:
    schedule.run_pending()
    time.sleep(1)