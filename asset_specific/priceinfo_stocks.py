import yfinance as yf
import pandas as pd
import concurrent.futures
import os

# 🔹 Load All Stocks Fundamentals Data (To Get Dates & Tickers)
all_stocks_fundamentals = pd.read_csv("stock_fundamentals.csv")
combined_financial_data = pd.read_csv("combined_financial_data.csv")
# 🔹 Extract Stock Symbols
STOCK_SYMBOLS = list(combined_financial_data[combined_financial_data["Asset Type"] == "Stock"]["Ticker"].unique())

# 🔹 Define Start Date
START_DATE = "2020-01-01"

# 🔹 Create Directory to Save Outputs
os.makedirs("technical_indicators", exist_ok=True)


# 🔹 Function to Fetch and Compute Technical Indicators
def compute_technical_indicators(ticker):
    try:
        print(f"📊 Processing {ticker}...")

        # Fetch Stock Data
        stock = yf.Ticker(ticker)
        df = stock.history(start=START_DATE)

        # Skip If No Data Found
        if df.empty:
            print(f"⚠️ No data found for {ticker}. Skipping...")
            return None

        # Reset Index and Convert Date to YYYY-MM-DD
        df.reset_index(inplace=True)
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

        # Compute Technical Indicators
        df["SMA_50"] = df["Close"].rolling(window=50).mean()
        df["SMA_200"] = df["Close"].rolling(window=200).mean()
        df["Middle Band"] = df["Close"].rolling(window=20).mean()
        df["Upper Band"] = df["Middle Band"] + 2 * df["Close"].rolling(window=20).std()
        df["Lower Band"] = df["Middle Band"] - 2 * df["Close"].rolling(window=20).std()

        delta = df["Close"].diff(1)
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))

        df["MACD"] = df["Close"].ewm(span=12, adjust=False).mean() - df["Close"].ewm(span=26, adjust=False).mean()
        df["MACD Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

        df["High-Low"] = df["High"] - df["Low"]
        df["High-Close"] = (df["High"] - df["Close"].shift(1)).abs()
        df["Low-Close"] = (df["Low"] - df["Close"].shift(1)).abs()
        df["True Range"] = df[["High-Low", "High-Close", "Low-Close"]].max(axis=1)
        df["ATR"] = df["True Range"].rolling(window=14).mean()

        df["OBV"] = (df["Volume"] * ((df["Close"] - df["Close"].shift(1)).apply(lambda x: 1 if x > 0 else -1))).cumsum()

        # Select Only Relevant Columns
        df = df[["Date", "Close", "SMA_50", "SMA_200", "Upper Band", "Middle Band", "Lower Band", "RSI", "MACD", "MACD Signal", "ATR", "OBV"]]
        df.dropna(inplace=True)

        # 🔹 Filter Only Dates Available in Fundamentals Data
        available_dates = all_stocks_fundamentals[all_stocks_fundamentals["Stock"] == ticker]["Date"]
        df = df[df["Date"].isin(available_dates)]

        # Set Date as Index
        df.set_index("Date", inplace=True)

        # Save CSV for Each Stock
        filename = f"technical_indicators/technical_indicators_{ticker}.csv"
        df.to_csv(filename, index=True)

        print(f"✅ {ticker} Data Saved ({len(df)} rows) → {filename}")
        return df

    except Exception as e:
        print(f"❌ Error processing {ticker}: {e}")
        return None


# 🔹 Run in Parallel for Speed Optimization
if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(compute_technical_indicators, STOCK_SYMBOLS)

    print("\n✅ All stocks processed successfully!")
