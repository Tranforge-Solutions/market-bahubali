import yfinance as yf

def get_news(ticker_symbol):
    print(f"Fetching news for {ticker_symbol}...")
    try:
        ticker = yf.Ticker(ticker_symbol)
        news = ticker.news
        if news:
            print(f"Found {len(news)} news items.")
            latest = news[0]
            print(f"Latest News Item: {latest}")
            print(f"Latest News: {latest.get('title')}")
            print(f"Link: {latest.get('link')}")
            print(f"Publisher: {latest.get('publisher')}")
        else:
            print("No news found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_news("RELIANCE.NS")
