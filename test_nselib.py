import nselib
from nselib import capital_market

print("Testing nselib for Bulk/Block Deals...")

try:
    # Fetch Bulk Deals for a specific period (e.g., last few days)
    # Note: nselib usually fetches for the whole market or specific date.
    # Let's try to get data for the last available trading day.
    
    # We don't have a direct "get by ticker" for bulk deals usually, it's a daily dump.
    # But let's check the library capabilities.
    
    print("Fetching Bulk Deals data...")
    # This might return a large DataFrame
    bulk_deals = capital_market.bulk_deal_data(period='1M')
    
    if bulk_deals is not None and not bulk_deals.empty:
        print(f"Fetched {len(bulk_deals)} records.")
        print("Columns:", bulk_deals.columns)
        
        # Filter for RELIANCE
        reliance_deals = bulk_deals[bulk_deals['SYMBOL'] == 'RELIANCE']
        if not reliance_deals.empty:
            print("\nReliance Deals:")
            print(reliance_deals.head())
        else:
            print("\nNo Reliance deals in last 1 month.")
            
        print("\nSample Data (First 5):")
        print(bulk_deals.head())
    else:
        print("No bulk deal data found.")

except Exception as e:
    print(f"Error: {e}")
