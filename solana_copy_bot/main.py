import csv
import pandas as pd
from solathon import Client
import time
from datetime import datetime
import numpy as np
import random
import socket

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
client = Client("https://api.mainnet-beta.solana.com")

def fetch_token_holdings(wallet_address):
    print(f"Fetching token holdings for wallet: {wallet_address}")
    try:
        response = client.get_token_accounts_by_owner(
            wallet_address,
            program_id="TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
            encoding="jsonParsed"
        )
        if response.get('result') is None or 'value' not in response['result']:
            print(f"Error fetching token accounts for {wallet_address}")
            return []
        token_accounts = response['result']['value']
        tokens = []

        for account in token_accounts:
            try:
                token_info = account['account']['data']['parsed']['info']['mint']
                tokens.append(token_info)
            except KeyError:
                continue
        print(f"Tokens found for wallet {wallet_address}: {tokens}")
        return tokens
    except Exception as e:
        if '429' in str(e) or 'rate limit' in str(e).lower():
            print(f"Rate limit hit while fetching token holdings for {wallet_address}. Retrying after delay.")
            time.sleep(5)
            return fetch_token_holdings(wallet_address)
        else:
            print(f"An error occurred while fetching token holdings for {wallet_address}: {e}")
            return []

def remove_duplicates(tokens):
    return list(set(tokens))

def fetch_transactions_history(wallet_address, limit=1000):
    print(f"Fetching transaction history for wallet: {wallet_address}")
    try:
        response = client.get_signatures_for_address(
            wallet_address,
            limit=limit
        )
        if 'result' not in response:
            print(f"Error fetching transaction history for {wallet_address}")
            return []
        transactions = response['result']
        print(f"Transactions found: {len(transactions)}")
        return transactions
    except socket.timeout:
        print(f"Request timed out for {wallet_address}. Retrying...")
        time.sleep(5)
        return fetch_transactions_history(wallet_address, limit)
    except Exception as e:
        if '429' in str(e) or 'rate limit' in str(e).lower():
            print(f"Rate limit hit while fetching transactions for {wallet_address}. Retrying after delay.")
            time.sleep(5)
            return fetch_transactions_history(wallet_address, limit)
        else:
            print(f"An error occurred while fetching transactions for {wallet_address}: {e}")
            return []

def analyze_transactions(transactions):
    print("Analyzing transactions to determine if wallet is a Bot or Human...")
    if len(transactions) < 2:
        print("Not enough transactions to analyze. Defaulting to 'Human'")
        return 'Human'

    timestamps = []
    amounts = []

    for tx in transactions:
        signature = tx['signature']
        try:
            tx_details = client.get_transaction(signature, encoding='json')
            if not tx_details.get('result'):
                continue

            block_time = tx_details['result'].get('blockTime')
            if block_time is None:
                continue

            timestamps.append(block_time)

            try:
                pre_balances = tx_details['result']['meta']['preTokenBalances']
                post_balances = tx_details['result']['meta']['postTokenBalances']
                if pre_balances and post_balances:
                    amount = int(post_balances[0]['uiTokenAmount']['amount']) - int(pre_balances[0]['uiTokenAmount']['amount'])
                    amounts.append(abs(amount))
            except (KeyError, IndexError, TypeError):
                continue
        except socket.timeout:
            print(f"Request timed out while fetching transaction {signature}. Skipping...")
            continue
        except Exception as e:
            if '429' in str(e) or 'rate limit' in str(e).lower():
                print(f"Rate limit hit while fetching transaction details for {signature}. Retrying after delay.")
                time.sleep(5)
                continue
            else:
                print(f"An error occurred while fetching transaction details for {signature}: {e}")
                continue

    if len(timestamps) < 2:
        print("Not enough valid transactions after filtering. Defaulting to 'Human'")
        return 'Human'

    timestamps = [datetime.fromtimestamp(ts) for ts in timestamps]
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

    if amounts:
        avg_amount = np.mean(amounts)
        std_amount = np.std(amounts)
        print(f"Average transaction amount: {avg_amount}")
        print(f"Standard deviation of transaction amounts: {std_amount}")
    else:
        avg_amount = 0
        std_amount = 0
        print("No transaction amounts found.")

    BOT_TX_FREQUENCY_THRESHOLD = 10
    BOT_INTERVAL_STD_THRESHOLD = 30
    BOT_AMOUNT_STD_THRESHOLD = 0.1 * avg_amount

    is_bot = False

    if tx_frequency > BOT_TX_FREQUENCY_THRESHOLD:
        print("Transaction frequency exceeds threshold. Marking as Bot.")
        is_bot = True
    if std_interval < BOT_INTERVAL_STD_THRESHOLD:
        print("Standard deviation of intervals below threshold. Marking as Bot.")
        is_bot = True
    if amounts and std_amount < BOT_AMOUNT_STD_THRESHOLD:
        print("Standard deviation of amounts below threshold. Marking as Bot.")
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


## Schedule the snapshot to run every 5 minutes
# Note: Be cautious with infinite loops in scripts. For debugging, you might want to run this once.
# while True:
#     snapshot_wallet_holdings()
#     time.sleep(300)  # Sleep for 5 minutes

# For testing purposes, let's run the snapshot once
# snapshot_wallet_holdings()
