# Stock Portfolio Tracker

CLI automation tool that connects to Finnhub API, stores portfolio data 
in PostgreSQL, and calculates real-time P&L.

## Commands
- add <SYMBOL> <QUANTITY> — add a transaction
- ls <SYMBOL> — list transactions for a stock
- ls+ — list all transactions 
- current-wl — display transactions and basic calculated data of a stock
- current-wl+ — display transactions and basic calculated data of all stock
- current-wl++ — display deep analysis of all the stocks and transactions
- remove-transaction — remove indivudual transaction within the database **2 step verification
- remove-stock — remove individual stock and all transaction related to that stock **2 step verification
- clear — clear all the data from the transactions , portfolio_summary , transaction_data , stocks **2 step verification
- get-info <SYMBOL> — return all the data of a company base on given symbol

## Setup
1. Clone the repo
2. Add Finnhub API key to .env
3. Set up PostgreSQL database
4. Run python main.py --help

## Tech Stack
- Python
- PostgreSQL (psycopg2)
- Finnhub REST API
- urllib3
- python-dotenv

## Features
- Live stock price fetching via Finnhub API
- Real-time P&L calculation
- Multi-command CLI architecture
- exception handling
- 2-step verification on destructive operations
- Automated portfolio summary tracking
