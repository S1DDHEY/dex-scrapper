import requests
import csv
import os
import schedule
import time

# Directory to store CSV files
output_dir = "./test_coin_data"
os.makedirs(output_dir, exist_ok=True)

# List of predefined pair addresses
pair_addresses = [
    "0x9d846CEeDDfd84c3B7010F29CdC513bdeFddA8b8",  # Replace with actual pair addresses
    "HqB7HKGiFhU5BViRKKNTCJiF1GAakyM5KQmiqeayb7FX"
]

def fetch_pair_data(pair_address):
    print(f"Fetching data for pair: {pair_address}...")

    # API endpoint for pair data
    url = f"https://api.dexscreener.com/latest/dex/search?q={pair_address}"

    # Output CSV file name
    csv_file = os.path.join(output_dir, f"{pair_address}.csv")

    try:
        # Fetch data from the API
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Check if 'pairs' key exists
        if 'pairs' not in data or len(data['pairs']) == 0:
            print(f"No data found for the pair address: {pair_address}.")
            return

        # Extract the first pair (assuming single match)
        pair = data['pairs'][0]

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

    except requests.exceptions.RequestException as e:
        print(f"API request failed for pair {pair_address}:", e)
    except KeyError as e:
        print(f"KeyError for pair {pair_address}: {e} - Check API response structure.")
    except Exception as e:
        print(f"An error occurred for pair {pair_address}: {e}")

# Schedule the tasks
schedule.every(1).minutes.do(lambda: [fetch_pair_data(pair) for pair in pair_addresses])

while True:
    schedule.run_pending()
    time.sleep(1)
