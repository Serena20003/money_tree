import yfinance as yf
import pandas as pd
import time

# Load the combined financial data
combined_financial_data = pd.read_csv("combined_financial_data.csv")

# Extract list of cryptocurrency tickers
CRYPTO_SYMBOLS = list(combined_financial_data[combined_financial_data["Asset Type"] == "Crypto"]["Ticker"])

# Initialize an empty list to store all crypto data
all_crypto_quarterly = []

# Loop through each crypto symbol
for symbol in CRYPTO_SYMBOLS:
    print(f"🔍 Fetching data for {symbol}...")

    try:
        # Fetch data from Yahoo Finance
        crypto = yf.Ticker(symbol)

        # Fetch historical prices (last 5 years of daily data)
        crypto_prices = crypto.history(period="5y")

        # Skip if no data is available
        if crypto_prices.empty:
            print(f"⚠️ No price data found for {symbol}. Skipping...")
            continue

        # Resample to quarterly frequency (every 3 months)
        crypto_quarterly = crypto_prices.resample("Q").agg({
            "Open": "first",   # First price in the quarter
            "High": "max",     # Highest price in the quarter
            "Low": "min",      # Lowest price in the quarter
            "Close": "last",   # Last price in the quarter
            "Volume": "sum"    # Total volume in the quarter
        })

        # Reset index and rename column
        crypto_quarterly = crypto_quarterly.reset_index().rename(columns={"Date": "Quarter End Date"})

        # Convert "Quarter End Date" to datetime format and remove timestamp
        crypto_quarterly["Quarter End Date"] = crypto_quarterly["Quarter End Date"].dt.strftime("%Y-%m-%d")

        # Add Crypto ticker column for identification
        crypto_quarterly["Crypto"] = symbol

        # Append to the list
        all_crypto_quarterly.append(crypto_quarterly)

        # Pause briefly to avoid hitting API rate limits
        time.sleep(1)

    except Exception as e:
        print(f"❌ Error processing {symbol}: {e}")

# Concatenate all Crypto data into a single DataFrame
df_all_crypto_quarterly = pd.concat(all_crypto_quarterly)

# Save to CSV
df_all_crypto_quarterly.to_csv("all_crypto_quarterly.csv", index=False)


