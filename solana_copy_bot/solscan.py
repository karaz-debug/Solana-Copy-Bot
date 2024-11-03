import csv
import pandas as pd
import requests
import time
from datetime import datetime
import numpy as np
import random

# Your Solscan API key
API_KEY = '21a1c71f8ee6431e8da639c629562d79'  # Replace with your actual API key

# Set the base URL for Solscan API
# For Public API
BASE_URL = 'https://api.solscan.io'

# For Pro API
# BASE_URL = 'https://pro-api.solscan.io/v1.0'

# Headers for authentication
headers = {
    'Accept': 'application/json',
    'token': API_KEY  # Use 'token' in lowercase
}

# File path to wallet addresses CSV
file_path = 'C:/Users/IQRA/Desktop/SOLANA-COPY-BOT/wallet_address.csv'
wallet_addresses = []

# Read Wallet Addresses from CSV
def read_wallet_addresses(file_path):
    print("Reading wallet addresses from CSV...")
    with open(file_path, mode='r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            wallet_addresses.append(row[0].strip())  # Remove any leading/trailing whitespace
    print(f"Total wallets read: {len(wallet_addresses)}")
    return wallet_addresses

# Call the function to populate wallet_addresses
wallet_addresses = read_wallet_addresses(file_path)

## Fetch Token Holdings for Each Wallet
def fetch_token_holdings(wallet_address):
    print(f"Fetching token holdings for wallet: {wallet_address}")
    try:
        url = f"{BASE_URL}/account/tokens?address={wallet_address}"
        response = requests.get(url, headers=headers)
        data = response.json()
        if data.get('success', False):
            tokens = [token['tokenAddress'] for token in data['data']]
            print(f"Tokens found for wallet {wallet_address}: {tokens}")
            return tokens
        else:
            print(f"Error fetching token accounts for {wallet_address}: {data.get('message')}")
            return []
    except Exception as e:
        print(f"An error occurred while fetching token holdings for {wallet_address}: {e}")
        return []

def remove_duplicates(tokens):
    return list(set(tokens))

## Fetch Transaction History for Each Wallet
def fetch_transactions_history(wallet_address, limit=50):
    print(f"Fetching transaction history for wallet: {wallet_address}")
    try:
        url = f"{BASE_URL}/account/transactions?address={wallet_address}&offset=0&limit={limit}"
        response = requests.get(url, headers=headers)
        data = response.json()
        if data.get('success', False):
            transactions = data['data']
            print(f"Transactions found: {len(transactions)}")
            return transactions
        else:
            print(f"Error fetching transactions for {wallet_address}: {data.get('message')}")
            return []
    except Exception as e:
        print(f"An error occurred while fetching transactions for {wallet_address}: {e}")
        return []

## Analyze Transactions to Differentiate Bots from Humans
def analyze_transactions(transactions):
    print("Analyzing transactions to determine if wallet is a Bot or Human...")
    if len(transactions) < 2:
        print("Not enough transactions to analyze. Defaulting to 'Human'")
        return 'Human'

    timestamps = []
    amounts = []

    for tx in transactions:
        try:
            block_time = tx.get('blockTime')
            if block_time is None:
                continue
            timestamps.append(datetime.fromtimestamp(block_time))

            # Solscan may not provide amount details directly in this endpoint.
            # Additional API calls may be needed to get transaction amounts.

        except Exception as e:
            print(f"An error occurred while processing transaction: {e}")
            continue

    if len(timestamps) < 2:
        print("Not enough valid transactions after filtering. Defaulting to 'Human'")
        return 'Human'

    timestamps.sort()
    time_intervals = [(timestamps[i+1] - timestamps[i]).total_seconds() for i in range(len(timestamps)-1)]
    print(f"Time intervals between transactions: {time_intervals}")

    avg_interval = np.mean(time_intervals)
    std_interval = np.std(time_intervals)
    print(f"Average interval: {avg_interval} seconds")
    print(f"Standard deviation of intervals: {std_interval} seconds")

    total_time = (timestamps[-1] - timestamps[0]).total_seconds() / 3600
    tx_frequency = len(timestamps) / total_time if total_time > 0 else len(timestamps)
    print(f"Transaction frequency: {tx_frequency} transactions per hour")

    # Since amounts are not available, we'll skip that analysis
    avg_amount = 0
    std_amount = 0

    BOT_TX_FREQUENCY_THRESHOLD = 10
    BOT_INTERVAL_STD_THRESHOLD = 30

    is_bot = False

    if tx_frequency > BOT_TX_FREQUENCY_THRESHOLD:
        print("Transaction frequency exceeds threshold. Marking as Bot.")
        is_bot = True
    if std_interval < BOT_INTERVAL_STD_THRESHOLD:
        print("Standard deviation of intervals below threshold. Marking as Bot.")
        is_bot = True

    wallet_type = 'Bot' if is_bot else 'Human'
    print(f"Wallet is classified as: {wallet_type}")
    return wallet_type

def write_to_csv(file_name, data):
    print(f"Writing data to {file_name}...")
    if not data:
        print(f"No data to write to {file_name}.")
        return
    keys = data[0].keys()
    with open(file_name, 'w', newline='', encoding='utf-8')  as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    print(f"Data written to {file_name} successfully.")

bot_data = []
human_data = []

for address in wallet_addresses:
    print(f"\nProcessing wallet: {address}")
    tokens = fetch_token_holdings(address)
    unique_tokens = remove_duplicates(tokens)

    transactions = fetch_transactions_history(address)
    wallet_type = analyze_transactions(transactions)

    wallet_info = {
        "Address": address,
        "Tokens": unique_tokens,
        "Type": wallet_type
    }

    if wallet_type == "Bot":
        bot_data.append(wallet_info)
    else:
        human_data.append(wallet_info)

    time.sleep(random.uniform(0.5, 1.5))

write_to_csv("bot_data.csv", bot_data)
write_to_csv("human_data.csv", human_data)

def snapshot_wallet_holdings():
    snapshoot_Data = []
    timestamp = datetime.now().isoformat()
    print(f"Taking snapshot at {timestamp}")
    for address in wallet_addresses:
        print(f"Snapshotting wallet: {address}")
        tokens = fetch_token_holdings(address)
        unique_tokens = remove_duplicates(tokens)

        snapshoot_Data.append({
            'timestamp': timestamp,
            'address': address,
            'tokens': unique_tokens
        })
        time.sleep(random.uniform(0.5, 1.5))
    with open('snapshot_data.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['timestamp', 'address', 'tokens'])
        if csvfile.tell() == 0:
            writer.writeheader()
        for data in snapshoot_Data:
            writer.writerow(data)
    print(f"Snapshot taken at {timestamp}")

# For testing purposes, let's run the snapshot once
snapshot_wallet_holdings()
