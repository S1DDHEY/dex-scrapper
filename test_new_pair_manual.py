import requests
import csv
import os
import schedule
import time
from dotenv import load_dotenv

# Directory to store CSV file
output_dir = "./test_coin_data"
os.makedirs(output_dir, exist_ok=True)
csv_file = os.path.join(output_dir, "pairs_with_socials.csv")

# Keep track of processed pairs
processed_pairs = set()

load_dotenv()

# Manually add pair addresses
manual_pairs = [
    "Fikoi5epMDNz848rQUbKVwRWTt9ubwroweSNbafAJLMD",
    "sp6DKKYq1MDXJi45QfbJyqvKwVxrNghTtZ9vH49pump",
    "6rgQRypjqs2rsrbuZ2AcQheV7r2MmtJwHNDsgMd7pump"
]

# Create CSV file if it doesn't exist
if not os.path.isfile(csv_file):
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Pair Address"])  # Header row

def process_manual_pairs():
    print("Processing manually added pairs...")
    for pair_address in manual_pairs:
        if pair_address not in processed_pairs:
            if fetch_pair_data(pair_address):
                processed_pairs.add(pair_address)

def fetch_pair_data(pair_address):
    print(f"Fetching data for pair: {pair_address}...")

    url = f"https://api.dexscreener.com/latest/dex/search?q={pair_address}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'pairs' not in data or not data['pairs']:
            print(f"No data found for the pair address: {pair_address}.")
            return False

        pair = data['pairs'][0]
        socials = pair.get("info", {}).get("socials", [])

        if not socials:
            print(f"Pair {pair_address} has data but no social links, skipping.")
            return False

        # Save only the pair address in CSV
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([pair_address])

        print(f"Pair {pair_address} saved.")
        return True

    except requests.exceptions.RequestException as e:
        print(f"API request failed for pair {pair_address}:", e)
    except Exception as e:
        print(f"An error occurred for pair {pair_address}: {e}")
    
    return False

# Schedule the task every 10 seconds
schedule.every(10).seconds.do(process_manual_pairs)

while True:
    schedule.run_pending()
    time.sleep(1)
