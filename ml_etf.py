import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# Load ETF historical data
etf_data = pd.read_csv("all_etf_quarterly.csv")
etf_data["Quarter End Date"] = pd.to_datetime(etf_data["Quarter End Date"])

# Load technical indicators
etf_technical = pd.read_csv("etf_technical_indicators.csv")
etf_technical["Date"] = pd.to_datetime(etf_technical["Date"])

# Load sentiment data
sentiment_data = pd.read_csv("sentiment_etfs.csv")
sentiment_data["Date"] = pd.to_datetime(sentiment_data["Date"])

# Aggregate sentiment data: Compute rolling average sentiment per ETF
sentiment_data["Sentiment Score"] = sentiment_data["Sentiment Score"].astype(float)
sentiment_data["Rolling Sentiment"] = (
    sentiment_data.groupby("ETF Ticker")["Sentiment Score"]
    .rolling(window=5, min_periods=1)
    .mean()
    .reset_index(level=0, drop=True)
)

# Forward fill missing sentiment values
sentiment_data["Rolling Sentiment"] = sentiment_data.groupby("ETF Ticker")["Rolling Sentiment"].ffill()

# Prepare the main dataset
features = ["Open", "High", "Low", "Volume", "Dividends"]
target = "Close"

# Create a new dataframe to hold aligned sentiment scores
aligned_sentiment = []

for index, row in etf_data.iterrows():
    etf = row["ETF"]
    date = row["Quarter End Date"]

    # Find the most recent sentiment data before or on the same date
    sentiment_score = sentiment_data[
        (sentiment_data["ETF Ticker"] == etf) & (sentiment_data["Date"] <= date)
    ]["Rolling Sentiment"].max()

    # Append to list (handle NaN if no sentiment exists)
    aligned_sentiment.append(sentiment_score if pd.notna(sentiment_score) else 0)

# Add sentiment feature to the dataset
etf_data["Sentiment Score"] = aligned_sentiment

# Prepare the feature matrix
X = etf_data[features + ["Sentiment Score"]].copy()  # Explicit copy
y = etf_data[target].copy()  # Explicit copy

# Handle missing values
X = X.fillna(0)  # Ensure this doesn't modify a slice
y = y.fillna(y.mean())  # Fill NaN target values with mean

# Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate performance
mae = mean_absolute_error(y_test, y_pred)

print(etf_data[["Close", "Sentiment Score"]].corr())

