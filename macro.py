import requests
import pandas as pd

FRED_API_KEY = "b37771365f10a212c6abf45a6e33ec50"
FRED_ENDPOINT = "https://api.stlouisfed.org/fred/series/observations"

def get_fred_data(series_id, label):
    url = f"{FRED_ENDPOINT}?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json"
    response = requests.get(url)
    data = response.json()
    
    # Check if data is available
    if "observations" in data and data["observations"]:
        df = pd.DataFrame(data["observations"])
        df["value"] = df["value"].astype(float)  # Convert value to float
        df.rename(columns={"value": label, "date": "Date"}, inplace=True)
        
        # Convert Date to datetime
        df["Date"] = pd.to_datetime(df["Date"])
        
        # Drop extra columns that cause merge conflicts
        df.drop(columns=["realtime_start", "realtime_end"], errors="ignore", inplace=True)
        
        return df
    else:
        return pd.DataFrame(columns=["Date", label])  # Empty DataFrame if no data

# 🔹 Fetch macroeconomic indicators
interest_rate = get_fred_data("FEDFUNDS", "Fed Rate (%)")
inflation_rate = get_fred_data("CPIAUCSL", "CPI")
unemployment_rate = get_fred_data("UNRATE", "Unemployment Rate (%)")
gdp_growth = get_fred_data("A191RL1Q225SBEA", "GDP Growth (%)")

# 🔹 Merge all datasets on "Date"
df_macro = (
    interest_rate.merge(inflation_rate, on="Date", how="outer")
    .merge(unemployment_rate, on="Date", how="outer")
    .merge(gdp_growth, on="Date", how="outer", suffixes=("_left", "_right"))
)

# 🔹 Drop rows with NaN values in essential columns
df_macro.dropna(subset=["Fed Rate (%)", "Unemployment Rate (%)", "CPI"], inplace=True)

# 🔹 Drop GDP Growth column if not needed
df_macro.drop(columns=["GDP Growth (%)"], inplace=True)

# 🔹 Filter data up to **January 1, 2020**
df_macro = df_macro[df_macro["Date"] >= "2020-01-01" ]

# 🔹 Sort by Date (latest data first)
df_macro.sort_values(by="Date", ascending=False, inplace=True)



print(df_macro)
df_macro.to_csv("macro_data.csv", index=False)
