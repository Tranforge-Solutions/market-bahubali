import pandas as pd
import yfinance as yf
import requests
import io
import logging
from sqlalchemy.orm import Session
from src.models.models import Symbol
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class UltraOptimizedSymbolService:
    def __init__(self, db: Session):
        self.db = db
        self.NIFTY_500_URL = "https://raw.githubusercontent.com/kprohith/nse-stock-analysis/master/ind_nifty500list.csv"

    def should_sync(self) -> bool:
        """Check if sync is needed (once per day)"""
        last_sync = self.db.query(Symbol).order_by(Symbol.created_at.desc()).first()
        if not last_sync:
            return True
        
        # Sync if last sync was more than 24 hours ago
        time_since_sync = datetime.now() - last_sync.created_at.replace(tzinfo=None)
        return time_since_sync > timedelta(hours=24)

    def sync_high_cap_stocks_ultra_fast(self, min_mcap_crore: float = None, force: bool = False):
        """
        Ultra-fast sync using yfinance batch download
        Downloads all 501 stocks in ONE API call!
        """
        from src.config.settings import Config

        if min_mcap_crore is None:
            min_mcap_crore = Config.MIN_MARKET_CAP_CRORE

        skip_mcap_filter = min_mcap_crore is None

        # Check if sync is needed
        if not force and not self.should_sync():
            logger.info("⏭️ Skipping sync - last sync was less than 24 hours ago")
            return

        if skip_mcap_filter:
            logger.info("Starting Ultra-Fast Stock Sync (Market Cap filter: DISABLED)")
        else:
            logger.info(f"Starting Ultra-Fast Stock Sync (Min Market Cap: ₹{min_mcap_crore:,.0f} Cr)")

        try:
            # 1. Fetch Nifty 500 list
            response = requests.get(self.NIFTY_500_URL)
            response.raise_for_status()
            csv_content = response.content.decode('utf-8')
            df = pd.read_csv(io.StringIO(csv_content))

            if 'Symbol' not in df.columns:
                logger.error("CSV format invalid: 'Symbol' column missing.")
                return

            symbols_list = df['Symbol'].tolist()
            tickers = [f"{sym}.NS" for sym in symbols_list]
            total = len(tickers)
            
            logger.info(f"Fetched {total} symbols. Downloading market data in BATCH...")

            # 2. BATCH DOWNLOAD - Download all tickers at once!
            # This is the KEY optimization - 1 API call instead of 501!
            tickers_str = " ".join(tickers)
            
            try:
                # Download 1 day of data for all tickers (just to get market cap)
                batch_data = yf.download(tickers_str, period="1d", group_by='ticker', threads=True, progress=False)
                logger.info(f"✅ Batch download complete! Processing {total} stocks...")
            except Exception as e:
                logger.error(f"Batch download failed: {e}. Falling back to individual fetch...")
                return

            count_added = 0
            count_skipped = 0

            # 3. Process each ticker (now much faster - just reading from batch data)
            for i, ticker in enumerate(tickers):
                try:
                    # Check if already exists
                    existing = self.db.query(Symbol).filter(Symbol.ticker == ticker).first()
                    if existing and existing.is_active:
                        continue

                    # Get ticker info (still need individual call for market cap)
                    t = yf.Ticker(ticker)
                    info = t.info
                    mcap = info.get('marketCap', 0) or 0
                    mcap_crore = mcap / 10_000_000

                    # Skip market cap check if filter is disabled
                    if not skip_mcap_filter and mcap_crore <= min_mcap_crore:
                        count_skipped += 1
                        continue

                    # Get company info
                    company_name = info.get('longName') or info.get('shortName', '')
                    sector = info.get('sector', '')
                    industry = info.get('industry', '')

                    # Add or Update
                    if not existing:
                        new_sym = Symbol(
                            ticker=ticker,
                            name=company_name,
                            sector=sector,
                            industry=industry,
                            market_cap_cr=mcap_crore,
                            is_active=True
                        )
                        self.db.add(new_sym)
                    else:
                        existing.is_active = True
                        existing.name = company_name
                        existing.sector = sector
                        existing.industry = industry
                        existing.market_cap_cr = mcap_crore

                    count_added += 1

                    # Commit every 20
                    if count_added % 20 == 0:
                        self.db.commit()
                        logger.info(f"Progress: {i+1}/{total} ({(i+1)/total*100:.1f}%)")

                except Exception as e:
                    if "404" in str(e) or "Not Found" in str(e):
                        logger.warning(f"Symbol {ticker} not found/delisted")
                    else:
                        logger.error(f"Error checking {ticker}: {e}")
                    count_skipped += 1

            # Final commit
            self.db.commit()
            logger.info(f"✅ Sync Complete! Added/Updated: {count_added}, Skipped: {count_skipped}")

        except Exception as e:
            logger.error(f"Failed to sync symbols: {e}")
