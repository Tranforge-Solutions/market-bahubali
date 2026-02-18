import yfinance as yf
import pandas as pd

tickers = ["RELIANCE.NS"]

for ticker in tickers:
    print(f"\n--- {ticker} ---")
    t = yf.Ticker(ticker)
    
    print("1. Major Holders:")
    try:
        mh = t.major_holders
        if mh is not None and not mh.empty:
            print(mh)
        else:
            print("None or Empty")
    except Exception as e:
        print(f"Error: {e}")

    print("\n2. Insider Purchases:")
    try:
        ip = t.insider_purchases
        if ip is not None and not ip.empty:
            print(ip.head())
        else:
            print("None or Empty")
    except Exception as e:
        print(f"Error: {e}")
