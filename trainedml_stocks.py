import os
import pandas as pd
import numpy as np
import google.generativeai as genai
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime

GOOGLE_GEMINI_API_KEY = "AIzaSyBna4L-UkOaaVb3cIx0d7_XQH1tpX9YnFw"  # Use environment variable
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)

def stock_model(stock_input):
    stock_ticker = stock_input  # Change this to any stock symbol

    # Load datasets
    df_technicals = pd.read_csv("all_technical_indicators_stocks.csv")
    df_fundamentals = pd.read_csv("stock_fundamentals.csv")
    df_sentiment = pd.read_csv("stock_sentiment_data.csv")

    # ✅ Convert 'Date' to datetime format
    df_technicals["Date"] = pd.to_datetime(df_technicals["Date"])
    df_fundamentals["Date"] = pd.to_datetime(df_fundamentals["Date"])
    df_sentiment["Date"] = pd.to_datetime(df_sentiment["Date"])

    # ✅ Fix Sentiment Score Column Name
    df_sentiment.rename(columns={"Sentiment Score": "Sentiment_Score"}, inplace=True)

    # ✅ Aggregate sentiment scores by Date & Stock
    df_sentiment = df_sentiment.groupby(["Date", "Stock Ticker"]).agg({"Sentiment_Score": "mean"}).reset_index()

    # ✅ Filter stock-specific data
    df_technicals = df_technicals[df_technicals["Stock"] == stock_ticker].drop(columns=["Stock"])
    df_fundamentals = df_fundamentals[df_fundamentals["Stock"] == stock_ticker].drop(columns=["Stock"])
    df_sentiment = df_sentiment[df_sentiment["Stock Ticker"] == stock_ticker].drop(columns=["Stock Ticker"])

    # ✅ Merge only Technicals & Fundamentals
    df_stock = df_technicals.merge(df_fundamentals, on="Date", how="inner")

    # ✅ Check if df_stock is empty before proceeding
    if df_stock.empty:
        raise ValueError(f"❌ No technical or fundamental data found for {stock_ticker}!")

    # ✅ Sort data by Date
    df_stock = df_stock.sort_values(by="Date")

    # ✅ Scale stock data (excluding Date column)
    scaler = MinMaxScaler()
    df_stock_scaled = df_stock.copy()
    df_stock_scaled[df_stock.columns.difference(["Date"])] = scaler.fit_transform(df_stock[df_stock.columns.difference(["Date"])])

    # ✅ Aggregate sentiment scores (Daily)
    df_sentiment_agg = df_sentiment.groupby("Date").agg({"Sentiment_Score": "mean"}).reset_index()
    df_sentiment_agg = df_sentiment_agg.sort_values(by="Date")

    # print("✅ Sentiment Data (Averaged by Date):")
    # print(df_sentiment_agg.tail())  # Debugging step

    # ✅ Prepare Data for Google Gemini AI
    stock_summary = df_stock_scaled.tail(48).to_string(index=False)  # Last 4 years of monthly data
    sentiment_summary = df_sentiment_agg.tail(48).to_string(index=False)  # Last 4 years of sentiment

    # ✅ AI Prompt: Separate Technicals+Fundamentals from Sentiment
    prompt = f"""
    Analyze the relationship between stock market data (technical + fundamentals) and sentiment analysis 
    for the past 4 years.

    ### Stock Data:
    {stock_summary}

    ### Sentiment Analysis:
    {sentiment_summary}

    Based on historical trends and sentiment analysis, predict the stock price movement for the next 3 months. 
    Provide reasoning for the prediction. 
    """

    # ✅ Generate Prediction from Google Gemini AI
    response = genai.GenerativeModel("gemini-1.5-pro").generate_content(prompt)

    return response.text
    # ✅ Display AI Prediction
    # print("\n📊 Google Gemini AI Prediction:\n")
    # print(response.text)

    # # ✅ Save Prediction to File
    # output_filename = f"{stock_ticker}_stock_prediction.txt"
    # with open(output_filename, "w") as f:
    #     f.write(response.text)

    # print(f"\n✅ Prediction saved to '{output_filename}'.")
