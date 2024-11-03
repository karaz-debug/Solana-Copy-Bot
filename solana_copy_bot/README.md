# Solana Copy Bot

## 🚀 Project Overview

The **Solana Copy Bot** is an automated system developed to analyze Solana (SOL) wallet activities and classify them as either bots or humans. Leveraging Python and the `solathon` library, the bot fetches token holdings and transaction histories from specified wallets, performs comprehensive analysis based on transaction patterns, and logs the results for further insights. The project is currently in the development stage, with ongoing enhancements to improve accuracy and functionality.

## 🔍 Features

- **Data Acquisition:**
  - **Wallet Address Management:** Reads and manages a list of Solana wallet addresses from a CSV file.
  - **Token Holdings Fetching:** Retrieves token holdings for each wallet using the Solathon API.
  - **Transaction History Retrieval:** Fetches transaction histories to analyze activity patterns.

- **Data Processing:**
  - **Duplicate Removal:** Ensures unique token holdings per wallet by eliminating duplicates.
  - **Transaction Analysis:** Analyzes transaction frequency, intervals, and amounts to determine wallet classification.
  - **Bot vs. Human Classification:** Implements logic to classify wallets based on predefined thresholds for transaction patterns.

- **Data Logging:**
  - **CSV Logging:** Records classified wallet data into separate CSV files (`bot_data.csv` and `human_data.csv`) for easy access and analysis.
  - **Snapshotting:** Captures periodic snapshots of wallet holdings, storing them with timestamps for historical tracking.

- **Error Handling:**
  - **Rate Limit Management:** Incorporates retry mechanisms and delays to handle API rate limits and ensure uninterrupted data fetching.
  - **Robust Exception Handling:** Manages various exceptions to maintain bot stability and reliability.

## 🛠 Installation

### Prerequisites

- **Python 3.9+**
- **Git:** [Download Git](https://git-scm.com/downloads)
- **Solathon Library:** [Solathon Documentation](https://github.com/your-repo/solathon) *(Ensure you have access and necessary credentials)*

### Steps

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/karz-debug/solana-copy-bot.git
   cd solana-copy-bot
