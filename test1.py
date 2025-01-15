import requests
import csv
import os
import json
import schedule
import time

def fetch_data():

    print("Fetching data...")

    # Enter the pair address or token symbol
    pair_address = "A3R8pxm228cUxXCRxAH1uDjwQZMiZKV3q6wxrUib9MQM"  # Replace with actual pair address or token symbol

    # API Endpoint
    url = f"https://api.dexscreener.com/latest/dex/search?q={pair_address}"

    # Output CSV file name
    csv_file = f"./coin_data/{pair_address}.csv"

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
        print("API request failed:", e)
    except KeyError as e:
        print(f"KeyError: {e} - Check API response structure.")
    except Exception as e:
        print("An error occurred:", e)



schedule.every(1).minutes.do(fetch_data)

while True:
    schedule.run_pending()
    time.sleep(1)
