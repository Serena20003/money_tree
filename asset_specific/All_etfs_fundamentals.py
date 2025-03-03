import yfinance as yf
import pandas as pd
import time

# Load the combined financial data
combined_financial_data = pd.read_csv("combined_financial_data.csv")

# Extract list of ETF tickers
ETF_SYMBOLS = list(combined_financial_data[combined_financial_data["Asset Type"] == "ETF"]["Ticker"])

# Initialize an empty list to store all data
all_etf_quarterly = []

# Loop through each ETF symbol
for symbol in ETF_SYMBOLS:
    print(f"🔍 Fetching data for {symbol}...")

    try:
        # Fetch data from Yahoo Finance
        etf = yf.Ticker(symbol)

        # Fetch historical prices (last 5 years of daily data)
        etf_prices = etf.history(period="5y")

        # Skip if no data is available
        if etf_prices.empty:
            print(f"⚠️ No price data found for {symbol}. Skipping...")
            continue

        # Resample to quarterly frequency (every 3 months)
        etf_quarterly = etf_prices.resample("Q").agg({
            "Open": "first",   # First price in the quarter
            "High": "max",     # Highest price in the quarter
            "Low": "min",      # Lowest price in the quarter
            "Close": "last",   # Last price in the quarter
            "Volume": "sum",   # Total volume in the quarter
            "Dividends": "sum" # Total dividends paid in the quarter
        })

        # Reset index and rename column
        etf_quarterly = etf_quarterly.reset_index().rename(columns={"Date": "Quarter End Date"})

        # Convert "Quarter End Date" to datetime format and remove timestamp
        etf_quarterly["Quarter End Date"] = etf_quarterly["Quarter End Date"].dt.strftime("%Y-%m-%d")

        # Add ETF ticker column for identification
        etf_quarterly["ETF"] = symbol

        # Append to the list
        all_etf_quarterly.append(etf_quarterly)

        # Pause briefly to avoid hitting API rate limits
        time.sleep(1)

    except Exception as e:
        print(f"❌ Error processing {symbol}: {e}")

# Concatenate all ETF data into a single DataFrame
df_all_etf_quarterly = pd.concat(all_etf_quarterly)

# Save to CSV
df_all_etf_quarterly.to_csv("all_etf_quarterly.csv", index=False)

