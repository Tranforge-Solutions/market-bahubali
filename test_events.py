import yfinance as yf
import pandas as pd
from datetime import datetime

def get_events(ticker_symbol):
    print(f"\nFetching events for {ticker_symbol}...")
    try:
        t = yf.Ticker(ticker_symbol)
        
        # 1. Calendar (Next Earnings)
        print("\n--- Calendar ---")
        if t.calendar:
            print(t.calendar)
        else:
            print("No calendar data.")

        # 2. Dividends (Recent/Upcoming)
        print("\n--- Dividends ---")
        divs = t.dividends
        if not divs.empty:
            print(divs.tail(5))
        else:
            print("No dividend history found.")

        # 3. Earnings Dates
        print("\n--- Earnings Dates ---")
        try:
            earnings = t.earnings_dates
            if earnings is not None and not earnings.empty:
                print(earnings.head(5))
            else:
                print("No earnings dates found.")
        except Exception as e:
            print(f"Error fetching earnings dates: {e}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Testing with a stock likely to have data
    get_events("RELIANCE.NS")
    get_events("TCS.NS")
