import asyncio
import aiohttp
import json
import os
import time
import schedule

def load_coin_addresses():
    """Load coin addresses from coins_with_socials.json."""
    json_path = "./test_coin_data/coins_with_socials.json"
    try:
        with open(json_path, 'r') as file:
            data = json.load(file)
            # If data is a list, return it directly
            if isinstance(data, list):
                return data
            # If data is a dict, try to get the coin addresses
            elif isinstance(data, dict):
                return data.get("coin_addresses", [])
            else:
                return []
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print("Error loading coin addresses:", e)
        return []

async def fetch_pair_data(session, pair_address):
    """Fetch data for a specific pair address and save it to a JSON file asynchronously."""
    url = f"https://api.dexscreener.com/latest/dex/search?q={pair_address}"
    json_file = f"./test_coin_data/{pair_address}.json"
    
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            
            # Write to file asynchronously (if needed, you might use aiofiles here)
            with open(json_file, 'w') as file:
                json.dump(data, file, indent=4)
            print(f"Updated data for {pair_address}")
    except Exception as e:
        print(f"API request failed for {pair_address}:", e)

async def update_all_coins_async():
    print("UPDATING DATA")
    """Fetch and update data for all coins in coins_with_socials.json concurrently."""
    coin_addresses = load_coin_addresses()
    if not coin_addresses:
        print("No coin addresses found. Skipping update.")
        return

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_pair_data(session, pair_address) for pair_address in coin_addresses]
        await asyncio.gather(*tasks)

def update_all_coins():
    """Wrapper to run the async update in the event loop."""
    asyncio.run(update_all_coins_async())

# Schedule the function to run every 10 seconds
schedule.every(10).seconds.do(update_all_coins)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
