import requests
import json
import time

def get_nse_bulk_deals(symbol):
    # NSE requires a cookie. We need to visit the homepage first.
    base_url = "https://www.nseindia.com"
    api_url = f"https://www.nseindia.com/api/snapshot-capital-market-bulk-deals-data?symbol={symbol}"
    # Alternative: https://www.nseindia.com/api/historical/bulk-deals?from=09-01-2026&to=09-02-2026&symbol=RELIANCE
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        print("Visiting Homepage to get cookies...")
        session.get(base_url, timeout=10)
        time.sleep(1)
        
        print(f"Fetching Bulk Deals for {symbol}...")
        # Note: NSE API endpoints change often. This is a best-guess for modern NSE site.
        # Let's try the market-wide bulk deals and filter, or symbol specific if available.
        # Actually, symbol specific bulk deals might not be unmatched.
        
        # Let's try the general bulk deals endpoint
        target_url = "https://www.nseindia.com/api/snapshot-capital-market-bulk-deals-data"
        response = session.get(target_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("Successfully fetched data.")
            # Verify structure
            # usually { "data": [ ... ] }
            deals = data.get('data', [])
            print(f"Found {len(deals)} total bulk deals today.")
            
            # Filter for symbol
            company_deals = [d for d in deals if d.get('symbol') == symbol]
            if company_deals:
                print(f"Found Deals for {symbol}:")
                for d in company_deals:
                     print(f"{d.get('date')} | {d.get('clientName')} | {d.get('buySell')} | Qty: {d.get('quantity')}")
            else:
                print(f"No bulk deals for {symbol} today.")
        else:
             print(f"Failed: {response.status_code}")
             print(response.text[:200])

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_nse_bulk_deals("RELIANCE")
