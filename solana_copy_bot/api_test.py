import os
import requests

# It's recommended to store API keys in environment variables for security
api_key = ''

if not api_key:
    raise ValueError("API key not found. Please set the BIRDEYE_API_KEY environment variable.")

url = "https://public-api.birdeye.so/v1/wallet/token_list"
params = {
    "wallet": "0xf584f8728b874a6a5c7a8d4d387c9aae9172d621"
}

headers = {
    "Accept": "application/json",
    "X-Chain": "solana",
    "Authorization": f"Bearer {api_key}"  # Adjust based on documentation
}

try:
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()  # Raises an HTTPError if the response was an error
    data = response.json()
    print(data)
except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err} - Response: {response.text}")
except Exception as err:
    print(f"An error occurred: {err}")
