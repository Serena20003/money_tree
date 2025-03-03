import yfinance as yf
import pandas as pd
import time

# Load the combined financial data
combined_financial_data = pd.read_csv("combined_financial_data.csv")

# Extract list of stock tickers
STOCK_SYMBOLS = list(combined_financial_data[combined_financial_data["Asset Type"] == "Stock"]["Ticker"])

# Initialize an empty list to store all data
all_stock_fundamentals = []

# Loop through each stock symbol
for symbol in STOCK_SYMBOLS:
    print(f"🔍 Fetching data for {symbol}...")

    try:
        # Fetch data from Yahoo Finance
        stock = yf.Ticker(symbol)

        # Extract financial statements
        income_statement = stock.financials.T  # Transpose for dates as index
        balance_sheet = stock.balance_sheet.T
        cash_flow = stock.cashflow.T

        # Skip if no data available
        if income_statement.empty or balance_sheet.empty or cash_flow.empty:
            #print(f"⚠️ No financial data found for {symbol}. Skipping...")
            continue

        # Extract historical data
        stock_fundamentals = pd.DataFrame({
            "Stock": symbol,
            "Date": income_statement.index,  # Use dates from income statement
            "P/E Ratio": income_statement.get("Net Income", pd.Series(dtype=float)) / balance_sheet.get("Stockholders Equity", pd.Series(dtype=float)),  
            "Earnings Per Share (EPS)": income_statement.get("Diluted EPS", pd.Series(dtype=float)),
            "Dividend Yield": stock.info.get("dividendYield", None),  # Pulled from stock.info (static value)
            "Return on Equity (ROE)": income_statement.get("Net Income", pd.Series(dtype=float)) / balance_sheet.get("Stockholders Equity", pd.Series(dtype=float)),
            "Debt-to-Equity Ratio (D/E)": balance_sheet.get("Total Debt", pd.Series(dtype=float)) / balance_sheet.get("Stockholders Equity", pd.Series(dtype=float)),
            "Free Cash Flow (FCF)": cash_flow.get("Cash Flow From Continuing Operating Activities", pd.Series(dtype=float)) - cash_flow.get("Capital Expenditure", pd.Series(dtype=float))
        })

        # Sort by Date (Most Recent First)
        stock_fundamentals.set_index("Date", inplace=True)
        stock_fundamentals.sort_index(ascending=False, inplace=True)
        stock_fundamentals.dropna(inplace=True)

        # Append to the list
        all_stock_fundamentals.append(stock_fundamentals)

        # Pause briefly to avoid hitting API rate limits
        time.sleep(1)  

    except Exception as e:
        print(f"❌ Error processing {symbol}: {e}")

# Concatenate all stock data into a single DataFrame
df_all_fundamentals = pd.concat(all_stock_fundamentals)
#print(df_all_fundamentals)

df_all_fundamentals.to_csv("stock_fundamentals.csv", index=True)

