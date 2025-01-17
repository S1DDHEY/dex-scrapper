import requests
import json

# Enter the pair address or token symbol
pair_address = "2VHjT2fQvVm8KE1L2PZThvm4zpUNQFb9zWGCVpmDu9GR"  # Replace with actual pair address or token symbol

# API Endpoint
url = f"https://api.dexscreener.com/latest/dex/search?q={pair_address}"

# Output JSON file name
json_file = f"./coin_data/{pair_address}.json"

try:
    # Fetch data from the API
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes
    data = response.json()

    # Check if 'pairs' key exists
    if 'pairs' not in data or len(data['pairs']) == 0:
        print("No data found for the given address.")
    else:
        # Extract the relevant data (pairs only)
        pairs_data = data['pairs']

        # Save to JSON file
        with open(json_file, 'w') as file:
            json.dump(pairs_data, file, indent=4)

        print(f"Data saved to {json_file}.")

except requests.exceptions.RequestException as e:
    print("API request failed:", e)
except KeyError as e:
    print(f"KeyError: {e} - Check API response structure.")
except Exception as e:
    print("An error occurred:", e)
