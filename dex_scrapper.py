import requests
import csv
import os
import time

# Enter the pair address or token symbol
pair_address = "A3R8pxm228cUxXCRxAH1uDjwQZMiZKV3q6wxrUib9MQM"  # Replace with actual pair address or token symbol

# API Endpoint
url = f"https://api.dexscreener.com/latest/dex/search?q={pair_address}"

# Output CSV file name
csv_file = "coin_data.csv"

# for i in range(3):

try:
    # Fetch data from the API
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes
    data = response.json()

    # Check if 'pairs' key exists
    if 'pairs' not in data or len(data['pairs']) == 0:
        print("No data found for the given address.")
    else:
        # Extract the first pair (assuming single match)
        pair = data['pairs'][0]

        # Extract required fields
        price_usd = pair.get('priceUsd', "N/A")
        price_native = pair.get('priceNative', "N/A")
        liquidity = pair['liquidity'].get('usd', "N/A")
        fdv = pair.get('fdv', "N/A")
        mkt_cap = pair.get('marketCap', "N/A")

        # Transactions
        txns = pair.get('txns', {}).get('h24', {})
        buys = txns.get('buys', "N/A")
        sells = txns.get('sells', "N/A")

        # Volumes
        volume = pair.get('volume', {}).get('h24', "N/A")

        # Prepare data for CSV
        row = [
            pair_address, price_usd, price_native, liquidity, fdv, mkt_cap, buys, sells, volume
        ]

        # Check if CSV exists
        file_exists = os.path.isfile(csv_file)

        # Write to CSV
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)

            # Write header if file is being created
            if not file_exists:
                writer.writerow([
                    "Pair Address", "Price (USD)", "Price (Native)", "Liquidity (USD)", "FDV", "Market Cap",
                    "24H Buys", "24H Sells", "24H Volume"
                ])

            # Write the data row
            writer.writerow(row)

        print(f"Data saved to {csv_file}.")

except requests.exceptions.RequestException as e:
    print("API request failed:", e)
except KeyError as e:
    print(f"KeyError: {e} - Check API response structure.")
except Exception as e:
    print("An error occurred:", e)

    # time.sleep(5) # 5 sec
