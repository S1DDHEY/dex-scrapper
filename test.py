import requests
import csv
import os
import time
import schedule

# Dictionary to store 5-minute interval data for computing 10-minute data
m5_data_cache = []

# Fetch data function
def fetch_data():
    print("Fetching data...")

    # Enter the pair address or token symbol
    pair_address = "A3R8pxm228cUxXCRxAH1uDjwQZMiZKV3q6wxrUib9MQM"  # Replace with actual pair address or token symbol

    # API Endpoint
    url = f"https://api.dexscreener.com/latest/dex/search?q={pair_address}"

    # Output CSV file name
    csv_file = f"./test_coin_data/{pair_address}.csv"

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

            # Transactions for m5
            txns = pair.get('txns', {})
            m5_buys = txns.get('m5', {}).get('buys', 0)
            m5_sells = txns.get('m5', {}).get('sells', 0)

            # Add the current m5 data to the cache
            m5_data_cache.append({'buys': m5_buys, 'sells': m5_sells})

            # Keep only the last 10 intervals in the cache
            if len(m5_data_cache) > 10:
                m5_data_cache.pop(0)

            # Compute m10 (sum of 1st and 6th, 2nd and 7th, etc.) if we have enough data
            m10_buys = "N/A"
            m10_sells = "N/A"
            if len(m5_data_cache) >= 10:
                m10_buys = m5_data_cache[0]['buys'] + m5_data_cache[5]['buys']
                m10_sells = m5_data_cache[0]['sells'] + m5_data_cache[5]['sells']

            # Prepare data for CSV
            row = [
                pair_address, m5_buys, m5_sells, m10_buys, m10_sells
            ]

            # Check if CSV exists
            file_exists = os.path.isfile(csv_file)

            # Write to CSV
            with open(csv_file, mode='a', newline='') as file:
                writer = csv.writer(file)

                # Write header if file is being created
                if not file_exists:
                    writer.writerow([
                        "Pair Address", "M5 Buys", "M5 Sells", "M10 Buys", "M10 Sells"
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

# Schedule to run every 1 minute
schedule.every(1).minutes.do(fetch_data)

while True:
    schedule.run_pending()
    time.sleep(1)
