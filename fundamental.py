#STOCKS
import requests
import pandas as pd

FMP_API_KEY = "SnDUCxCa9cPquuQ7o343nctcm46oTgYc"
SYMBOL = "AAPL"  # Change to any stock
ETF_SYMBOL = "LQD"
COMMODITY_SYMBOL = "ES=F"
BOND_SYMBOL = "LQD"
CRYPTO_SYMBOL = "BTC-USD"
REIT_SYMBOL = "VNQ" 

# Function to fetch financial data from FMP
def get_fmp_data(statement_type, symbol, limit=20):
    url = f"https://financialmodelingprep.com/api/v3/{statement_type}/{symbol}?limit={limit}&apikey={FMP_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if isinstance(data, list):
        return pd.DataFrame(data)  # Convert JSON to DataFrame
    else:
        print(f"❌ ERROR: Unable to fetch {statement_type} data!")
        return pd.DataFrame()  # Return empty DataFrame if request fails

# Fetch Historical Financial Statements
income_statement = get_fmp_data("income-statement", SYMBOL)
balance_sheet = get_fmp_data("balance-sheet-statement", SYMBOL)
cash_flow = get_fmp_data("cash-flow-statement", SYMBOL)
ratios = get_fmp_data("ratios", SYMBOL)

# Extract Required Data
stock_fundamentals = pd.DataFrame({
    "Date": income_statement["date"],
    "P/E Ratio": ratios.get("priceEarningsRatio", pd.Series(dtype=float)),
    "Earnings Per Share (EPS)": income_statement.get("eps", pd.Series(dtype=float)),
    "Dividend Yield": ratios.get("dividendYield", pd.Series(dtype=float)),
    "Return on Equity (ROE)": ratios.get("returnOnEquity", pd.Series(dtype=float)),
    "Debt-to-Equity Ratio (D/E)": ratios.get("debtEquityRatio", pd.Series(dtype=float)),
    "Free Cash Flow (FCF)": cash_flow.get("freeCashFlow", pd.Series(dtype=float))
})

# Sort Data by Date (Most Recent First)
stock_fundamentals.set_index("Date", inplace=True)
stock_fundamentals.sort_index(ascending=False, inplace=True)

#print("Stocks: ")
#print(stock_fundamentals)
stock_fundamentals.to_csv("stock_fundamentals.csv", index=True)

###########################################################################
#ETFS and INDEX FUNDS

import yfinance as yf

etf = yf.Ticker(ETF_SYMBOL)

# Fetch historical prices (daily)
etf_prices = etf.history(period="5y")  # Fetch last 5 years of daily data

# Resample to quarterly frequency (every 3 months)
etf_quarterly = etf_prices.resample("Q").agg({
    "Open": "first",   # First price in the quarter
    "High": "max",     # Highest price in the quarter
    "Low": "min",      # Lowest price in the quarter
    "Close": "last",   # Last price in the quarter
    "Volume": "sum",   # Total volume in the quarter
    "Dividends": "sum" # Total dividends paid in the quarter

})

etf_quarterly = etf_quarterly.reset_index().rename(columns={"Date": "Quarter End Date"})

# Convert "Quarter End Date" to datetime format and remove timestamp
etf_quarterly["Quarter End Date"] = pd.to_datetime(etf_quarterly["Quarter End Date"]).dt.strftime("%Y-%m-%d")

# Set "Quarter End Date" as the index
etf_quarterly.set_index("Quarter End Date", inplace=True)


etf_fundamentals = pd.DataFrame.from_dict({
    "ETF Symbol": [ETF_SYMBOL],
    "ETF Name": [etf.info.get("longName", "N/A")],
    "P/E Ratio": [etf.info.get("trailingPE", "N/A")],
    "Dividend Yield": [etf.info.get("dividendYield", "N/A")],
    "Net Assets ($B)": [etf.info.get("totalAssets", "N/A") / 1e9],  # Convert to billions
    "ETF Category": [etf.info.get("category", "N/A")]
})

etf_quarterly = pd.DataFrame(etf_quarterly)
# print("ETF/Index Funds: ")
# print(etf_quarterly)
# print(etf_fundamentals)
etf_quarterly.to_csv("etf_quarterly.csv", index=True)
etf_quarterly.to_csv("etf_quarterly.csv", index=True)

###############################################################################################################
#Commodities 

commodity = yf.Ticker(COMMODITY_SYMBOL)

# Fetch historical daily prices and resample to quarterly
commodity_prices = commodity.history(period="5y")  # Fetch last 10 years of daily data

# Resample to quarterly data
commodity_quarterly = commodity_prices.resample("Q").agg({
    "Open": "first",
    "High": "max",
    "Low": "min",
    "Close": "last",
    "Volume": "sum"
})

# Reset index and rename the date column
commodity_quarterly = commodity_quarterly.reset_index().rename(columns={"Date": "Quarter End Date"})

# Convert "Quarter End Date" to datetime format and remove timestamp
commodity_quarterly["Quarter End Date"] = pd.to_datetime(commodity_quarterly["Quarter End Date"]).dt.strftime("%Y-%m-%d")

# Set "Quarter End Date" as the index
commodity_quarterly.set_index("Quarter End Date", inplace=True)
commodity_quarterly = pd.DataFrame(commodity_quarterly)
# print("Commodity DF:")
# print(commodity_quarterly)
commodity_quarterly.to_csv("commodity_quarterly.csv", index=True)

######################################################################################
#BONDS

bond = yf.Ticker(BOND_SYMBOL)

# Fetch historical daily prices and resample to quarterly
bond_prices = bond.history(period="5y")  # Fetch last 10 years of daily data

# Resample to quarterly data
bond_quarterly = bond_prices.resample("Q").agg({
    "Open": "first",
    "High": "max",
    "Low": "min",
    "Close": "last",
})

# Reset index and rename the date column
bond_quarterly = bond_quarterly.reset_index().rename(columns={"Date": "Quarter End Date"})

# Convert "Quarter End Date" to datetime format and remove timestamp
bond_quarterly["Quarter End Date"] = pd.to_datetime(bond_quarterly["Quarter End Date"]).dt.strftime("%Y-%m-%d")

# Set "Quarter End Date" as the index
bond_quarterly.set_index("Quarter End Date", inplace=True)
bond_quarterly = pd.DataFrame(bond_quarterly)

# print("Bonds: ")
# print(bond_quarterly)
bond_quarterly.to_csv("bond.csv", index=True)

#####################################################################################################################
#CRYPTO

crypto = yf.Ticker(CRYPTO_SYMBOL)
crypto_prices = crypto.history(period="5y")  # Fetch last 10 years of daily data

# Resample to quarterly data
crypto_quarterly = crypto_prices.resample("Q").agg({
    "Open": "first",
    "High": "max",
    "Low": "min",
    "Close": "last",
    "Volume": "sum"
})

# Reset index and rename the date column
crypto_quarterly = crypto_quarterly.reset_index().rename(columns={"Date": "Quarter End Date"})

# Convert "Quarter End Date" to datetime format and remove timestamp
crypto_quarterly["Quarter End Date"] = pd.to_datetime(crypto_quarterly["Quarter End Date"]).dt.strftime("%Y-%m-%d")

# Set "Quarter End Date" as the index
crypto_quarterly.set_index("Quarter End Date", inplace=True)

crypto_quarterly= pd.DataFrame(crypto_quarterly)
# print("Crypto: ")
# print(crypto_quarterly)
crypto_quarterly.to_csv("crypto_quarterly.csv", index=True)

#####################################################################################################################
#REITS

reit = yf.Ticker(REIT_SYMBOL)

# Fetch historical daily prices and resample to quarterly
reit_prices = reit.history(period="5y")  # Fetch last 10 years of daily data

# Resample to quarterly data
reit_quarterly = reit_prices.resample("Q").agg({
    "Open": "first",
    "High": "max",
    "Low": "min",
    "Close": "last",
    "Volume": "sum",
    "Dividends": "sum"
})

# Reset index and rename the date column
reit_quarterly = reit_quarterly.reset_index().rename(columns={"Date": "Quarter End Date"})

# Convert "Quarter End Date" to datetime format and remove timestamp
reit_quarterly["Quarter End Date"] = pd.to_datetime(reit_quarterly["Quarter End Date"]).dt.strftime("%Y-%m-%d")

# Set "Quarter End Date" as the index
reit_quarterly.set_index("Quarter End Date", inplace=True)


# Convert to DataFrame and Merge with Quarterly Prices
reit_quarterly = pd.DataFrame(reit_quarterly)

# print("REITS: ")
# print(reit_quarterly)
reit_quarterly.to_csv("reit_quarterly.csv", index=True)

