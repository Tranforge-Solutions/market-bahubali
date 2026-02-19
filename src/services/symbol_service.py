import pandas as pd
import yfinance as yf
import requests
import io
import logging
from sqlalchemy.orm import Session
from src.models.models import Symbol

logger = logging.getLogger(__name__)

class SymbolService:
    def __init__(self, db: Session):
        self.db = db
        # URL for Nifty 500 list
        self.NIFTY_500_URL = "https://raw.githubusercontent.com/kprohith/nse-stock-analysis/master/ind_nifty500list.csv"

    def sync_high_cap_stocks(self, min_mcap_crore: float = None):
        """
        Fetches Nifty 500 list, checks Market Cap, and activates stocks > min_mcap_crore.
        """
        from src.config.settings import Config
        
        if min_mcap_crore is None:
            min_mcap_crore = Config.MIN_MARKET_CAP_CRORE
        
        logger.info(f"Starting High Cap Stock Sync (Min Market Cap: ₹{min_mcap_crore:,.0f} Crore)...")
        
        try:
            # 1. Fetch CSV
            response = requests.get(self.NIFTY_500_URL)
            response.raise_for_status()
            csv_content = response.content.decode('utf-8')
            
            df = pd.read_csv(io.StringIO(csv_content))
            
            if 'Symbol' not in df.columns:
                logger.error("CSV format invalid: 'Symbol' column missing.")
                return

            symbols_list = df['Symbol'].tolist()
            total = len(symbols_list)
            logger.info(f"fetched {total} symbols from Nifty 500 list. Checking Market Caps...")

            count_added = 0
            count_skipped = 0

            # 2. Iterate and Check
            # Note: Checking 500 individually is slow. 
            # Optimization: We check one by one for reliability in this demo.
            for i, sym in enumerate(symbols_list):
                ticker = f"{sym}.NS"
                
                # Check if already exists and is active? 
                # We might want to re-check mcap periodically, but for now let's check new ones.
                existing = self.db.query(Symbol).filter(Symbol.ticker == ticker).first()
                if existing and existing.is_active:
                     # Already tracked
                     continue

                try:
                    t = yf.Ticker(ticker)
                    # Use fast_info if available for speed, else info
                    info = t.info
                    mcap = info.get('marketCap', 0)
                    
                    if mcap is None:
                        mcap = 0
                        
                    mcap_crore = mcap / 10_000_000
                    
                    if mcap_crore > min_mcap_crore:
                        # Add or Update
                        if not existing:
                            new_sym = Symbol(ticker=ticker, is_active=True)
                            self.db.add(new_sym)
                            logger.info(f"✅ Added {ticker} (Mcap: {mcap_crore:.2f} Cr)")
                        else:
                            existing.is_active = True
                            logger.info(f"🔄 Reactivated {ticker} (Mcap: {mcap_crore:.2f} Cr)")
                        
                        count_added += 1
                        # Commit every 5 to save progress
                        if count_added % 5 == 0:
                            self.db.commit()
                    else:
                        count_skipped += 1
                        # logger.debug(f"Skipped {ticker} (Mcap: {mcap_crore:.2f} Cr)")

                except Exception as e:
                    # Log 404s as Warnings (expected for some delisted stocks)
                    if "404" in str(e) or "Not Found" in str(e):
                        logger.warning(f"Symbol {ticker} not found/delisted. Skipping.")
                    else:
                        logger.error(f"Error checking {ticker}: {e}")
                
                # Log progress
                if (i+1) % 50 == 0:
                    logger.info(f"Processed {i+1}/{total} symbols...")

            self.db.commit()
            logger.info(f"Sync Complete. Added/Active: {count_added}, Skipped: {count_skipped}")

        except Exception as e:
            logger.error(f"Failed to sync symbols: {e}")
