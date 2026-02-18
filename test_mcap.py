import yfinance as yf

def check_mcap(ticker):
    try:
        t = yf.Ticker(ticker)
        # Fast info fetch
        info = t.info
        mcap = info.get('marketCap')
        currency = info.get('currency')
        
        print(f"\n{ticker}:")
        print(f"  Currency: {currency}")
        print(f"  Market Cap: {mcap}")
        
        if mcap:
            # 1 Crore = 10,000,000
            mcap_crore = mcap / 10_000_000
            print(f"  Market Cap in Cr: {mcap_crore:.2f}")
            
            if mcap_crore > 10000:
                print("  ✅ > 10,000 Cr")
            else:
                print("  ❌ < 10,000 Cr")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_mcap("RELIANCE.NS") # Large Cap
    check_mcap("SUZLON.NS")   # Mid/Small Cap check
    check_mcap("IDEA.NS")
