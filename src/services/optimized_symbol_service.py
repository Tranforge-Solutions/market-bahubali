import pandas as pd
import yfinance as yf
import requests
import io
import logging
from sqlalchemy.orm import Session
from src.models.models import Symbol
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class OptimizedSymbolService:
    def __init__(self, db: Session):
        self.db = db
        self.db_lock = Lock()  # Thread-safe database access
        self.NIFTY_500_URL = "https://raw.githubusercontent.com/kprohith/nse-stock-analysis/master/ind_nifty500list.csv"

    def should_sync(self) -> bool:
        """Check if sync is needed (once per day)"""
        last_sync = self.db.query(Symbol).order_by(Symbol.created_at.desc()).first()
        if not last_sync:
            return True
        
        # Sync if last sync was more than 24 hours ago
        time_since_sync = datetime.now() - last_sync.created_at.replace(tzinfo=None)
        return time_since_sync > timedelta(hours=24)

    def _fetch_single_stock(self, sym: str, min_mcap_crore: float, skip_mcap_filter: bool):
        """Fetch single stock data - thread-safe"""
        ticker = f"{sym}.NS"
        
        try:
            # Check if already exists (read-only, no lock needed)
            with self.db_lock:
                existing = self.db.query(Symbol).filter(Symbol.ticker == ticker).first()
                if existing and existing.is_active:
                    return None  # Already tracked
            
            # Fetch data (no lock needed - external API call)
            t = yf.Ticker(ticker)
            info = t.info
            mcap = info.get('marketCap', 0) or 0
            mcap_crore = mcap / 10_000_000
            
            # Skip market cap check if filter is disabled
            if not skip_mcap_filter and mcap_crore <= min_mcap_crore:
                return None
            
            # Get company info
            company_name = info.get('longName') or info.get('shortName', '')
            sector = info.get('sector', '')
            industry = info.get('industry', '')
            
            return {
                'ticker': ticker,
                'name': company_name,
                'sector': sector,
                'industry': industry,
                'market_cap_cr': mcap_crore,
                'existing': existing
            }
            
        except Exception as e:
            if "404" in str(e) or "Not Found" in str(e):
                logger.warning(f"Symbol {ticker} not found/delisted")
            else:
                logger.error(f"Error checking {ticker}: {e}")
            return None

    def sync_high_cap_stocks_optimized(self, min_mcap_crore: float = None, max_workers: int = 10):
        """
        Optimized sync using multithreading
        max_workers: Number of parallel threads (default: 10)
        """
        from src.config.settings import Config

        if min_mcap_crore is None:
            min_mcap_crore = Config.MIN_MARKET_CAP_CRORE

        skip_mcap_filter = min_mcap_crore is None
        
        if skip_mcap_filter:
            logger.info(f"Starting Optimized Stock Sync ({max_workers} threads, Market Cap filter: DISABLED)")
        else:
            logger.info(f"Starting Optimized Stock Sync ({max_workers} threads, Min Market Cap: ₹{min_mcap_crore:,.0f} Cr)")

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
            logger.info(f"Fetched {total} symbols. Processing with {max_workers} threads...")

            count_added = 0
            count_skipped = 0
            processed = 0

            # 2. Process in parallel using ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                future_to_symbol = {
                    executor.submit(self._fetch_single_stock, sym, min_mcap_crore, skip_mcap_filter): sym 
                    for sym in symbols_list
                }
                
                # Process completed tasks
                for future in as_completed(future_to_symbol):
                    processed += 1
                    result = future.result()
                    
                    if result:
                        # Add/Update in database (thread-safe)
                        with self.db_lock:
                            if not result['existing']:
                                new_sym = Symbol(
                                    ticker=result['ticker'],
                                    name=result['name'],
                                    sector=result['sector'],
                                    industry=result['industry'],
                                    market_cap_cr=result['market_cap_cr'],
                                    is_active=True
                                )
                                self.db.add(new_sym)
                                logger.info(f"✅ Added {result['ticker']} - {result['name']} (Mcap: {result['market_cap_cr']:.2f} Cr)")
                            else:
                                result['existing'].is_active = True
                                result['existing'].name = result['name']
                                result['existing'].sector = result['sector']
                                result['existing'].industry = result['industry']
                                result['existing'].market_cap_cr = result['market_cap_cr']
                                logger.info(f"🔄 Updated {result['ticker']} - {result['name']} (Mcap: {result['market_cap_cr']:.2f} Cr)")
                            
                            count_added += 1
                            
                            # Commit every 10 to save progress
                            if count_added % 10 == 0:
                                self.db.commit()
                    else:
                        count_skipped += 1
                    
                    # Log progress
                    if processed % 50 == 0:
                        logger.info(f"Progress: {processed}/{total} ({(processed/total)*100:.1f}%)")

            # Final commit
            with self.db_lock:
                self.db.commit()
            
            logger.info(f"Sync Complete! Added/Updated: {count_added}, Skipped: {count_skipped}")
            logger.info(f"Performance: Processed {total} stocks using {max_workers} threads")

        except Exception as e:
            logger.error(f"Failed to sync symbols: {e}")
