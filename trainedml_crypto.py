import numpy as np
import tensorflow as tf
import pandas as pd
from datetime import timedelta
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def crypto_model(crypto_ticker):
    df_macro = pd.read_csv("macro_data.csv", index_col="Date", parse_dates=True)

    df_crypto_technicals = pd.read_csv("crypto_technical_indicators.csv", index_col="Date", parse_dates=True)
    df_crypto_sentiment = pd.read_csv("sentiment_crypto.csv", index_col="Date", parse_dates=True)
    df_crypto_fundamentals = pd.read_csv("all_crypto_quarterly.csv", index_col="Quarter End Date", parse_dates=True)

    df_crypto_fundamentals.reset_index(inplace=True)  # Reset index to access "Quarter End Date"
    df_crypto_fundamentals.rename(columns={"Quarter End Date": "Date"}, inplace=True)
    df_crypto_fundamentals["Date"] = pd.to_datetime(df_crypto_fundamentals["Date"]).dt.strftime("%Y-%m-%d")

    df_crypto_technicals.reset_index(inplace=True)  # Reset index to access "Date"
    df_crypto_technicals["Date"] = pd.to_datetime(df_crypto_technicals["Date"])

    if 'Date' in df_crypto_technicals.columns:
        df_crypto_technicals.set_index('Date', inplace=True)  # Set 'Date' as index
    else:
        raise KeyError("The DataFrame does not have a 'Date' column")

    df_crypto_technicals = df_crypto_technicals.apply(pd.to_numeric, errors='coerce')

    df_crypto_technicals = df_crypto_technicals.ffill()  # Forward-fill missing values

    df_crypto_quarterly = df_crypto_technicals.resample("Q").mean().reset_index()

    df_crypto_quarterly["Date"] = df_crypto_quarterly["Date"] + pd.offsets.QuarterEnd(0)

    df_crypto_quarterly["Date"] = df_crypto_quarterly["Date"].dt.strftime("%Y-%m-%d")
    df_crypto_fundamentals["Date"] = pd.to_datetime(df_crypto_fundamentals["Date"]).dt.strftime("%Y-%m-%d")

    df_crypto = df_crypto_fundamentals.merge(df_crypto_quarterly, on="Date", how="inner")

    df_macro.reset_index(inplace=True)
    df_macro["Date"] = pd.to_datetime(df_macro["Date"])  # Convert to datetime

    # ✅ Now subtract 1 day safely
    df_macro["Date"] = df_macro["Date"] - timedelta(days=1)

    # ✅ Convert back to string format if needed
    df_macro["Date"] = df_macro["Date"].dt.strftime("%Y-%m-%d")

    df_crypto = df_crypto.merge(df_macro, on="Date", how="inner")  # Use "left" to keep all crypto records


    df_crypto = df_crypto.sort_values(by="Date")
    missing_values = df_crypto.isnull().sum()

    # Filter and print only columns that have NaN values
    columns_with_nan = missing_values[missing_values > 0]
    df_crypto.drop(columns="Crypto_y", inplace=True)
    #print(df_crypto)

    crypto_name = crypto_ticker  
    crypto_specific_df = df_crypto[df_crypto["Crypto_x"] == crypto_name].copy()

    crypto_specific_df = crypto_specific_df.drop(columns=["Crypto_x"])  # No need for categorical data

    # ✅ Step 3: Create the Target Variable (Shift Open Price)
    crypto_specific_df["Future_Open"] = crypto_specific_df["Open"].shift(-1)




    # ✅ Step 4: Remove Rows with Missing Values (Caused by Shift)
    crypto_specific_df = crypto_specific_df.dropna()


    print(f"Shape of crypto_specific_df: {crypto_specific_df.shape}")
    print(crypto_specific_df.head())

    # ✅ Step 5: Scale Features (Normalize All Columns Except Date & Target Variable)
    scaler = MinMaxScaler()
    scaled_features = scaler.fit_transform(crypto_specific_df.drop(columns=["Date", "Open", "Future_Open"]))

    # ✅ Step 6: Scale Target Variable (Future Open Price)
    target_scaler = MinMaxScaler(feature_range=(0, 1))  # Ensure full range
    scaled_target = target_scaler.fit_transform(crypto_specific_df["Future_Open"].values.reshape(-1, 1))


    # # ✅ Use StandardScaler instead of MinMaxScaler
    # scaler = StandardScaler()
    # scaled_features = scaler.fit_transform(crypto_specific_df.drop(columns=["Date", "Open", "Future_Open"]))

    # target_scaler = StandardScaler()  # Scale the target variable
    # scaled_target = target_scaler.fit_transform(crypto_specific_df["Future_Open"].values.reshape(-1, 1))


    # ✅ Step 7: Define Features (X) & Target (y)
    X, y = scaled_features, scaled_target

    # ✅ Step 8: Reshape X for LSTM (samples, time steps, features)
    X = np.reshape(X, (X.shape[0], 1, X.shape[1]))  # LSTM expects 3D input

    # ✅ Step 9: Split Data into Train & Test Sets (80% Training, 20% Testing)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # Build the LSTM model
    model = Sequential([
        LSTM(60, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
        Dropout(0.2),  # Reduce dropout to allow better learning
        LSTM(60, return_sequences=False),
        Dropout(0.2),
        Dense(30, activation="relu"),
        Dense(1)
    ])

    # Compile the model
    model.compile(optimizer="adam", loss="mean_squared_error")

    # Train the model
    history = model.fit(X_train, y_train, epochs=50, batch_size=16, validation_data=(X_test, y_test), verbose=1)

    # Predict future open price using the latest available data
    latest_data = X[-1].reshape(1, 1, X.shape[2])
    predicted_open_scaled = model.predict(latest_data)
    predicted_open = target_scaler.inverse_transform(predicted_open_scaled.reshape(-1, 1))[0][0]




    # ✅ Start with the latest available data
    future_predictions = []


    # ✅ Predict Open Price for 2 Quarters (6 months)
    for i in range(7):  # 2 quarters ahead
        # Predict the next Open price
        predicted_open_scaled = model.predict(latest_data)

        # Convert back to actual price
        predicted_open = target_scaler.inverse_transform(predicted_open_scaled.reshape(-1, 1))[0][0]
        future_predictions.append(predicted_open)

        # Prepare the predicted Open price as input for the next prediction
        latest_data = np.append(latest_data[:, :, 1:], predicted_open_scaled.reshape(1, 1, 1), axis=2)

    return future_predictions

    # ✅ Print Predicted Open Prices for Next 2 Quarters
    # for i, price in enumerate(future_predictions):
    #     print(f"Predicted Open Price for {3*(i+1)} months ahead: ${price:.2f}")

