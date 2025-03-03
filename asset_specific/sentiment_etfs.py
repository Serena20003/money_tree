import requests
import pandas as pd
import concurrent.futures
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
from bs4 import BeautifulSoup
import time

# 🔹 Load the combined financial data
combined_financial_data = pd.read_csv("combined_financial_data.csv")

# 🔹 Extract list of ETF tickers
ETF_SYMBOLS = list(combined_financial_data[combined_financial_data["Asset Type"] == "ETF"]["Ticker"])

# 🔹 Set up VADER Sentiment Analyzer
vader_analyzer = SentimentIntensityAnalyzer()

# 🔹 Define start date filter (Only news from 2020 onwards)
start_date = datetime(2020, 1, 1)

# 🔹 Function to fetch Google News RSS (Faster than APIs)
def fetch_google_news(etf_ticker):
    try:
        url = f"https://news.google.com/rss/search?q={etf_ticker}+ETF&hl=en-US&gl=US&ceid=US:en"
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, "xml")  # Parse XML
        
        articles = []
        for item in soup.find_all("item"):
            title = item.title.text
            link = item.link.text
            pub_date = item.pubDate.text
            description = item.description.text

            published_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
            if published_date >= start_date:
                articles.append({
                    "ETF Ticker": etf_ticker,
                    "Date": published_date.strftime("%Y-%m-%d"),
                    "Title": title,
                    "Content": description,
                    "URL": link
                })
        
        return articles
    
    except Exception as e:
        print(f"⚠️ Google News error for {etf_ticker}: {e}")
        return []

# 🔹 Function to analyze sentiment using VADER
def analyze_sentiment(article):
    score = vader_analyzer.polarity_scores(article["Content"])["compound"]
    category = "Positive" if score > 0.05 else "Negative" if score < -0.05 else "Neutral"
    article["Sentiment Score"] = score
    article["Sentiment Category"] = category
    return article

# 🔹 Parallel Processing for Speed (Fetch & Analyze in Parallel)
news_data = []

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    # ✅ Fetch news articles for all ETFs in parallel
    all_articles = list(executor.map(fetch_google_news, ETF_SYMBOLS))

    # ✅ Flatten nested lists
    all_articles = [article for sublist in all_articles for article in sublist]

    # ✅ Run sentiment analysis in parallel
    news_data = list(executor.map(analyze_sentiment, all_articles))

    # ✅ Sleep to avoid request limits
    time.sleep(2)

# 🔹 Convert to DataFrame
df_etf_sentiment = pd.DataFrame(news_data)

# ✅ Save to CSV
df_etf_sentiment.to_csv("sentiment_etfs.csv", index=False)


print("\n✅ Sentiment Data saved successfully as 'etf_sentiment_data.csv'!")
