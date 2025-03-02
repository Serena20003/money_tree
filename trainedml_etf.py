import pandas as pd
import numpy as np
from datetime import timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor


def etf_model(etf_ticker):
    # ✅ Load the datasets
    df_macro = pd.read_csv("macro_data.csv", index_col="Date", parse_dates=True)

    df_stock_fundamentals = pd.read_csv("stock_fundamentals.csv", index_col="Date", parse_dates=True)
    df_stock_technicals = pd.read_csv("all_technical_indicators_stocks.csv", index_col="Date", parse_dates=True)
    df_stock_sentiment = pd.read_csv("stock_sentiment_data.csv", index_col="Date", parse_dates=True)

    df_etf_technicals = pd.read_csv("etf_technical_indicators.csv", index_col="Date", parse_dates=True)
    df_etf_sentiment = pd.read_csv("sentiment_etfs.csv", index_col="Date", parse_dates=True)
    df_etf_fundamentals = pd.read_csv("all_etf_quarterly.csv", index_col="Quarter End Date", parse_dates=True)

    # ✅ Ensure Date is Consistent for ETF Data
    df_etf_fundamentals.reset_index(inplace=True)  # Reset index to access "Quarter End Date"
    df_etf_fundamentals.rename(columns={"Quarter End Date": "Date"}, inplace=True)
    df_etf_fundamentals["Date"] = pd.to_datetime(df_etf_fundamentals["Date"]).dt.strftime("%Y-%m-%d")

    df_etf_technicals.reset_index(inplace=True)  # Reset index to access "Date"
    df_etf_technicals["Date"] = pd.to_datetime(df_etf_technicals["Date"])

    # ✅ Ensure 'Date' column exists
    if 'Date' in df_etf_technicals.columns:
        df_etf_technicals.set_index('Date', inplace=True)  # Set 'Date' as index
    else:
        raise KeyError("The DataFrame does not have a 'Date' column")

    # ✅ Ensure all data is numeric where necessary
    df_etf_technicals = df_etf_technicals.apply(pd.to_numeric, errors='coerce')

    # ✅ Resample Technicals to Quarterly
    df_etf_quarterly = df_etf_technicals.resample("Q").mean().reset_index()


    # Ensure Date alignment to quarter-end dates
    df_etf_quarterly["Date"] = df_etf_quarterly["Date"] + pd.offsets.QuarterEnd(0)

    # Convert date columns to string format AFTER performing date arithmetic
    df_etf_quarterly["Date"] = df_etf_quarterly["Date"].dt.strftime("%Y-%m-%d")
    df_etf_fundamentals["Date"] = pd.to_datetime(df_etf_fundamentals["Date"]).dt.strftime("%Y-%m-%d")


    # Fill missing values in technical indicators before resampling
    df_etf_technicals = df_etf_technicals.ffill()

    # Merge DataFrames on "Date"
    df_etf = df_etf_fundamentals.merge(df_etf_quarterly, on="Date", how="inner")

    # Check missing values
    # print("\nMissing values per column:\n", df_etf.isna().sum())


    ### end of new code

    # ✅ Merge on "Date"
    # EXPERIMENT df_etf = df_etf_fundamentals.merge(df_etf_quarterly, on="Date", how="left")
    df_etf.drop(columns=["ETF_y"], inplace=True)
    # df_etf.drop(columns=["ETF"], inplace=True)

    df_etf.dropna(inplace=True)

    df_macro.reset_index(inplace=True)
    df_macro['Date'] = df_macro['Date'] - timedelta(days=1)
    

    # print(df_macro)
    df_macro['Date'] = pd.to_datetime(df_macro['Date'])
    df_etf['Date'] = pd.to_datetime(df_etf['Date'])

    # Merge on the quarterly dates
    df_etf = df_etf.merge(df_macro, on='Date', how='inner')


    #print("\nMerged ETF Data Sample:\n", df_etf)

    ######################################################################

    # import numpy as np
    # import tensorflow as tf
    # from tensorflow.keras.models import Sequential
    # from tensorflow.keras.layers import LSTM, Dense, Dropout
    # from sklearn.preprocessing import MinMaxScaler
    # from sklearn.model_selection import train_test_split

    # # Ensure data is sorted by date
    # original_etf_df = df_etf.sort_values(by="Date")
    # #print(etf_df.dtypes)
    # etf_name = "SPY"  # Change this to the ETF you want to test
    # etf_specific_df = original_etf_df[original_etf_df["ETF_x"] == etf_name].copy()
    # # Normalize the feature data for LSTM (helps with training stability)
    # etf_specific_df = etf_specific_df.drop(columns = ['ETF_x'])
    # etf_df = etf_specific_df
    # print(etf_df)


    # scaler = MinMaxScaler()
    # scaled_features = scaler.fit_transform(etf_df.drop(columns=["Date", "Open", "Future_Open"]))

    # # Scale target variable (Future Open price)
    # target_scaler = MinMaxScaler()
    # scaled_target = target_scaler.fit_transform(etf_df["Future_Open"].values.reshape(-1, 1))

    # # Define X (features) and y (target)
    # X, y = scaled_features, scaled_target


    # # Reshape for LSTM input: (samples, time steps, features)
    # X = np.reshape(X, (X.shape[0], 1, X.shape[1]))
    # # X = X[:-1]
    # # Split data into train and test sets (80/20)
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    import numpy as np
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.model_selection import train_test_split

    # ✅ Ensure data is sorted by date
    df_etf = df_etf.sort_values(by="Date")

    # ✅ Step 1: Filter for a Specific ETF (e.g., SPY)
    etf_name = etf_ticker  # Change this to any ETF symbol you want
    etf_specific_df = df_etf[df_etf["ETF_x"] == etf_name].copy()

    # ✅ Step 2: Drop Non-Numeric Column
    etf_specific_df = etf_specific_df.drop(columns=["ETF_x"])  # No need for categorical data

    # ✅ Step 3: Create the Target Variable (Shift Open Price)
    etf_specific_df["Future_Open"] = etf_specific_df["Open"].shift(-1)

    # ✅ Step 4: Remove Rows with Missing Values (Caused by Shift)
    etf_specific_df = etf_specific_df.dropna()

    # ✅ Step 5: Scale Features (Normalize All Columns Except Date & Target Variable)
    scaler = MinMaxScaler()
    scaled_features = scaler.fit_transform(etf_specific_df.drop(columns=["Date", "Open", "Future_Open"]))

    # ✅ Step 6: Scale Target Variable (Future Open Price)
    target_scaler = MinMaxScaler()
    scaled_target = target_scaler.fit_transform(etf_specific_df["Future_Open"].values.reshape(-1, 1))

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
    latest_data = X[-1].reshape(1, 1, X.shape[2])  # Get last known data

    # ✅ Predict Open Price for 2 Quarters (6 months)
    for i in range(7):  
        # Predict the next Open price
        predicted_open_scaled = model.predict(latest_data)

        # Convert back to actual price
        predicted_open = target_scaler.inverse_transform(predicted_open_scaled.reshape(-1, 1))[0][0]
        future_predictions.append(predicted_open)

        # Prepare the predicted Open price as input for the next prediction
        latest_data = np.append(latest_data[:, :, 1:], predicted_open_scaled.reshape(1, 1, 1), axis=2)

    # ✅ Print Predicted Open Prices for Next 2 Quarters
    return future_predictions

    

