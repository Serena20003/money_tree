import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# 🔹 Load Crypto Tickers from CSV
crypto_fundamentals = pd.read_csv("all_crypto_quarterly.csv")
CRYPTO_SYMBOLS = crypto_fundamentals["Crypto"].dropna().unique().tolist()  # Get unique crypto tickers

# 🔹 Define start date
start_date = "2020-01-01"

# 🔹 Function to Fetch Crypto Price Data & Compute Technical Indicators
def get_crypto_data(ticker):
    try:
        crypto = yf.Ticker(ticker)
        df = crypto.history(start=start_date)

        # ✅ Skip if no data is available
        if df.empty:
            print(f"⚠️ No data for {ticker}. Skipping...")
            return None

        # 🔹 Reset Index to Make Date a Column
        df.reset_index(inplace=True)

        # 🔹 Convert Date to Proper Format (YYYY-MM-DD)
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

        # 🔹 Compute Technical Indicators

        # 1️⃣ Moving Averages (SMA)
        df["SMA_50"] = df["Close"].rolling(window=50).mean()
        df["SMA_200"] = df["Close"].rolling(window=200).mean()

        # 2️⃣ Bollinger Bands
        df["Middle Band"] = df["Close"].rolling(window=20).mean()
        df["Upper Band"] = df["Middle Band"] + 2 * df["Close"].rolling(window=20).std()
        df["Lower Band"] = df["Middle Band"] - 2 * df["Close"].rolling(window=20).std()

        # 3️⃣ Relative Strength Index (RSI)
        delta = df["Close"].diff(1)
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))

        # 4️⃣ MACD (Moving Average Convergence Divergence)
        df["MACD"] = df["Close"].ewm(span=12, adjust=False).mean() - df["Close"].ewm(span=26, adjust=False).mean()
        df["MACD Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

        # 5️⃣ Average True Range (ATR)
        df["High-Low"] = df["High"] - df["Low"]
        df["High-Close"] = (df["High"] - df["Close"].shift(1)).abs()
        df["Low-Close"] = (df["Low"] - df["Close"].shift(1)).abs()
        df["True Range"] = df[["High-Low", "High-Close", "Low-Close"]].max(axis=1)
        df["ATR"] = df["True Range"].rolling(window=14).mean()

        # 6️⃣ On-Balance Volume (OBV)
        df["OBV"] = (df["Volume"] * ((df["Close"] - df["Close"].shift(1)).apply(lambda x: 1 if x > 0 else -1))).cumsum()

        # 🔹 Keep Only Relevant Columns
        df = df[["Date", "Close", "SMA_50", "SMA_200", "Upper Band", "Middle Band", "Lower Band", "RSI", "MACD", "MACD Signal", "ATR", "OBV"]]

        # 🔹 Drop Missing Values
        df.dropna(inplace=True)

        # 🔹 Set "Date" as Index & Add Crypto Symbol
        df.set_index("Date", inplace=True)
        df["Crypto"] = ticker  # Add ticker as a column

        print(f"✅ Processed {ticker} ({len(df)} rows)")
        return df

    except Exception as e:
        print(f"❌ Error processing {ticker}: {e}")
        return None

# 🔹 Fetch Data for All Cryptos in Parallel
all_crypto_data = []
with ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(get_crypto_data, CRYPTO_SYMBOLS)
    all_crypto_data.extend([r for r in results if r is not None])  # Keep only valid results

# 🔹 Combine All Crypto Data
df_all_cryptos = pd.concat(all_crypto_data, ignore_index=False)

# 🔹 Save to CSV
df_all_cryptos.to_csv("crypto_technical_indicators.csv", index=True)
print("✅ Crypto Technical Indicators Saved: 'crypto_technical_indicators.csv'")
