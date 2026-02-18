import yfinance as yf
import pandas as pd

ticker = "RELIANCE.NS"
print(f"--- Researching Data for {ticker} ---")
symbol = yf.Ticker(ticker)

print("\n[1] Major Holders:")
try:
    print(symbol.major_holders)
except Exception as e:
    print(e)

print("\n[2] Institutional Holders:")
try:
    print(symbol.institutional_holders)
except Exception as e:
    print(e)

print("\n[3] Mutual Fund Holders:")
try:
    print(symbol.mutualfund_holders)
except Exception as e:
    print(e)

print("\n[4] Insider Purchases:")
try:
    print(symbol.insider_purchases)
except Exception as e:
    print(e)

print("\n[5] Insider Transactions:")
try:
    print(symbol.insider_transactions)
except Exception as e:
    print(e)
    
print("\n[6] News (checking for bulk deals keywords):")
try:
    for item in symbol.news:
        print(f"- {item['content']['title']}")
except Exception as e:
    print(e)
