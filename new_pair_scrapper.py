import requests
import csv
import os
import schedule
import time
import dontshare

# Directory to store CSV files
output_dir = "./coin_data"
os.makedirs(output_dir, exist_ok=True)

# Keep track of processed pairs
processed_pairs = set()

def fetch_new_pairs():
    # print("Fetching new pairs...")  #<--------------------------------------------------------------------------

    # BirdEye API endpoint for new pairs
    new_pairs_url = "https://public-api.birdeye.so/defi/v2/tokens/new_listing?limit=5&meme_platform_enabled=false"

    headers = {
        "accept": "application/json",
        "x-chain": "solana",  # Update the chain if necessary
        "X-API-KEY": f"{dontshare.API_KEY}"  # Include the API key in the headers
    }

    try:
        # Fetch new pairs data
        response = requests.get(new_pairs_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Navigate through the response to get the list of items
        items = data.get("data", {}).get("items", [])

        if not items:
            print("No new pairs found.")
            return

        for item in items:
            # Extract token address
            pair_address = item.get("address")  # Ensure key matches the BirdEye API response
            if not pair_address:
                print("Token address not found in an item.")
                continue

            # Skip if pair has already been processed
            if pair_address in processed_pairs:
                # print(f"Skipping {pair_address} as it has already been processed.") #<--------------------------------------------------------------------------
                continue

            # Fetch data for the pair using Dex Screener API
            if fetch_pair_data(pair_address):
                processed_pairs.add(pair_address)

    except requests.exceptions.RequestException as e:
        print("API request for new pairs failed:", e)
    except Exception as e:
        print("An error occurred while fetching new pairs:", e)

def fetch_pair_data(pair_address):
    # print(f"Fetching data for pair: {pair_address}...") #<--------------------------------------------------------------------------

    # Dex Screener API endpoint for pair data
    url = f"https://api.dexscreener.com/latest/dex/search?q={pair_address}"

    # Output CSV file name
    csv_file = os.path.join(output_dir, f"{pair_address}.csv")

    try:
        # Fetch data from the API
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Check if 'pairs' key exists
        if 'pairs' not in data or not data['pairs']:
            # print(f"No data found for the pair address: {pair_address}.") #<--------------------------------------------------------------------------
            return False

        # Extract the first pair (assuming single match)
        pair = data['pairs'][0]

        # Check if socials exist in 'info' section
        socials = pair.get("info", {}).get("socials", [])
        if not socials:
            # print(f"Skipping {pair_address} as it has no social links.") #<--------------------------------------------------------------------------
            return False

        # Extract required fields
        price_usd = pair.get('priceUsd', "N/A")
        fdv = pair.get('fdv', "N/A")
        mkt_cap = pair.get('marketCap', "N/A")
        liquidity = pair['liquidity'].get('usd', "N/A")

        # Transactions for m5, h1, h6, h24
        txns = pair.get('txns', {})
        buys_sells = {
            'm5': {
                'buys': txns.get('m5', {}).get('buys', "N/A"),
                'sells': txns.get('m5', {}).get('sells', "N/A")
            },
            'h1': {
                'buys': txns.get('h1', {}).get('buys', "N/A"),
                'sells': txns.get('h1', {}).get('sells', "N/A")
            },
            'h6': {
                'buys': txns.get('h6', {}).get('buys', "N/A"),
                'sells': txns.get('h6', {}).get('sells', "N/A")
            },
            'h24': {
                'buys': txns.get('h24', {}).get('buys', "N/A"),
                'sells': txns.get('h24', {}).get('sells', "N/A")
            }
        }

        # Volumes for m5, h1, h6, h24
        volumes = {
            'm5': pair.get('volume', {}).get('m5', "N/A"),
            'h1': pair.get('volume', {}).get('h1', "N/A"),
            'h6': pair.get('volume', {}).get('h6', "N/A"),
            'h24': pair.get('volume', {}).get('h24', "N/A")
        }

        # Prepare data for CSV
        row = [
            pair_address, price_usd, fdv, mkt_cap, liquidity,
            buys_sells['m5']['buys'], buys_sells['m5']['sells'],
            buys_sells['h1']['buys'], buys_sells['h1']['sells'],
            buys_sells['h6']['buys'], buys_sells['h6']['sells'],
            buys_sells['h24']['buys'], buys_sells['h24']['sells'],
            volumes['m5'], volumes['h1'], volumes['h6'], volumes['h24']
        ]

        # Check if CSV exists
        file_exists = os.path.isfile(csv_file)

        # Write to CSV
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)

            # Write header if file is being created
            if not file_exists:
                writer.writerow([
                    "Pair Address", "Price (USD)", "FDV", "Market Cap", "Liquidity (USD)",
                    "M5 Buys", "M5 Sells", "H1 Buys", "H1 Sells", "H6 Buys", "H6 Sells", "H24 Buys", "H24 Sells",
                    "Volume M5", "Volume H1", "Volume H6", "Volume H24"
                ])

            # Write the data row
            writer.writerow(row)

        print(f"Data saved to {csv_file}.")
        return True

    except requests.exceptions.RequestException as e:
        print(f"API request failed for pair {pair_address}:", e)
    except KeyError as e:
        print(f"KeyError for pair {pair_address}: {e} - Check API response structure.")
    except Exception as e:
        print(f"An error occurred for pair {pair_address}: {e}")
    return False

# Schedule the tasks
schedule.every(10).seconds.do(fetch_new_pairs)

while True:
    schedule.run_pending()
    time.sleep(1)
