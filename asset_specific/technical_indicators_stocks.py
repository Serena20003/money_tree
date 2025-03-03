import os
import pandas as pd

# 🔹 Define the folder path where the CSVs are stored
technical_folder = "technical_indicators"

# 🔹 Dictionary to store data for each stock
technical_data = {}

# 🔹 Loop through all files in the folder
for filename in os.listdir(technical_folder):
    if filename.endswith(".csv"):  # Ensure it's a CSV file
        stock_symbol = filename.replace("technical_indicators_", "").replace(".csv", "")  # Extract ticker
        file_path = os.path.join(technical_folder, filename)
        
        # Load the CSV into a DataFrame
        df = pd.read_csv(file_path, index_col="Date", parse_dates=True)
        
        # Store in dictionary
        technical_data[stock_symbol] = df

print(f"\n✅ Loaded {len(technical_data)} technical indicator datasets!")
# 🔹 Concatenate all technical indicators into one DataFrame
all_technical_df = pd.concat(technical_data.values(), keys=technical_data.keys(), names=["Stock", "Date"])

# 🔹 Save it for later use
all_technical_df.to_csv("all_technical_indicators_stocks.csv")
print("\n✅ All technical indicators combined into 'all_technical_indicators.csv'!")
