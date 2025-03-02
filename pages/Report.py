import streamlit as st
# # connecting to database
# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi
# uri = "mongodb+srv://" + st.secrets['MONGODB_ROOT_USER_NAME'] + ":" + st.secrets['MONGODB_ROOT_USER_PASSWORD'] + "@cluster0.pa5rn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# # Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))

# st.session_state.isLoading = True
# st.session_state.reportReady = False

st.session_state.stocks = []
# test
st.session_state.predictions = []

from Start import Setup, DataValidation
from algorithm import match_investors
from database import User, Investment, get_investments_from_csv
# from trainedml_crypto import crypto_model
from trainedml_etf import etf_model
from trainedml_stocks import stock_model

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



Setup()
st.session_state.predictions = [[],[],[]]

def ShowPred(rank):
    st.subheader("Predictions")
    for i in range(len(st.session_state.predictions[rank])):
        st.write(str((i+1)*3) + " months: " + str(st.session_state.predictions[rank][i]))

def GetStocks():
    # get from function
    user = User()
    user.parse_information_tester(st.session_state.user_input)
    # get investment info
    if ('opportunities' not in st.session_state):
        st.session_state.opportunities = get_investments_from_csv()
    st.session_state.stocks = match_investors(user, st.session_state.opportunities)

def SetStockPrediction(rank, ticker, type):
    if (type == "ETF"):
        st.session_state.predictions[rank] = etf_model(ticker) # list of 3,6,9,12,15,18,21 month prediction based on the ticker
    else:
        st.session_state.predictions[rank] = crypto_model(ticker) # list of 3,6,9,12,15,18,21 month prediction based on the ticker

def ShowStock(rank):
    # make cute display of cards
    # collapsable details to reduce reloading
    st.header("Investment #" + str(rank+1) + ": " + st.session_state.stocks[rank][1].name)
    # if crypto, etf
    if st.session_state.stocks[rank][1].asset_type == "ETF" or st.session_state.stocks[rank][1].asset_type == "Crypto":
        SetStockPrediction(rank, st.session_state.stocks[rank][1].ticker, st.session_state.stocks[rank][1].asset_type)
        st.subheader("Predictions")
        col1, col2 = st.columns(2, border=True)
        # most recent prediction
        mstRecent = ""
        if (st.session_state.predictions[rank][0] < 0):
            mstRecent = "-"
        mstRecent += "$" + str(abs(st.session_state.predictions[rank][0]))
        col1.metric("3 months", mstRecent)
        # second most recent prediction
        mst2Recent = ""
        if (st.session_state.predictions[rank][1] < 0):
            mst2Recent = "-"
        mst2Recent += "$" + str(abs(st.session_state.predictions[rank][1]))
        col2.metric("6 months", mst2Recent, str((st.session_state.predictions[rank][1]-st.session_state.predictions[rank][0])/abs(st.session_state.predictions[rank][0])*100)+"%")
    
    # if stock, show description
    if st.session_state.stocks[rank][1].asset_type == "Stock":
        with st.expander("Stock Description"):
            st.write(stock_model(st.session_state.stocks[rank][1].ticker))

    with st.expander("Further information"):
        st.write(st.session_state.stocks[rank][1])
        ShowPred(rank)

def PrintUser():
    # income, savings, ratio, duration, commitment, target, appetite, max_drawdown, skill_level
    user = st.session_state.user_input
    with st.expander("Your information"):
        st.write(f"Income: ${user[0]}")
        st.write(f"Savings: ${user[1]}")
        st.write(f"Debt to Income Ratio: ${user[2]}")
        st.write(f"Desired Investment Duration: ${user[3]}")
        st.write(f"Monthly Investment Commitment: ${user[4]}")
        st.write(f"Target Return Expectation: ${user[5]}")
        st.write(f"Risk Appetite: ${user[6]}")
        st.write(f"Maximum Drawdown level: ${user[7]}")
        st.write(f"Confidence Level in Investing: ${user[8]}")

if 'user_input' not in st.session_state or DataValidation() != None:
    st.write("Please head back to Start page to let us know your investment preferences!")
    if st.button("Take me back!"):
        st.switch_page("Start.py")
else:
    if (st.session_state.name != ""):
        st.title("Hi, " + st.session_state.name + "!")
    else:
        st.title("Hi!")
    PrintUser()
    st.title("Now, here's your top 3 investments.")
    GetStocks()
    ShowStock(0)
    ShowStock(1)
    ShowStock(2)
    
    
    # while st.session_state.isLoading:
    #     st.spinner(text="Generating Report...")
    #     if st.session_state.reportReady:
    #         st.session_state.isLoading = False