import requests
import pandas as pd
import concurrent.futures
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
from bs4 import BeautifulSoup

# 🔹 Set up VADER Sentiment Analyzer
vader_analyzer = SentimentIntensityAnalyzer()

# 🔹 Define stock ticker & start date filter
stocks = ["AAPL"]
start_date = datetime(2020, 1, 1)

# 🔹 Function to fetch Google News RSS (Faster than APIs)
def fetch_google_news(stock_ticker):
    try:
        url = f"https://news.google.com/rss/search?q={stock_ticker}+stock&hl=en-US&gl=US&ceid=US:en"
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
                    "Stock Ticker": stock_ticker,
                    "Date": published_date.strftime("%Y-%m-%d"),
                    "Title": title,
                    "Content": description,
                    "URL": link
                })
        
        return articles
    
    except Exception as e:
        print(f"⚠️ Google News error for {stock_ticker}: {e}")
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

with concurrent.futures.ThreadPoolExecutor() as executor:
    # ✅ Fetch news articles for all stocks in parallel
    all_articles = list(executor.map(fetch_google_news, stocks))

    # ✅ Flatten nested lists
    all_articles = [article for sublist in all_articles for article in sublist]

    # ✅ Run sentiment analysis in parallel
    news_data = list(executor.map(analyze_sentiment, all_articles))

# 🔹 Convert to DataFrame
df_sentiment = pd.DataFrame(news_data)

#print(df_sentiment[df_sentiment["Sentiment Category"] == 'Negative'])
# 🔹 Save to CSV
df_sentiment.to_csv("sentiment_data.csv", index=False)






