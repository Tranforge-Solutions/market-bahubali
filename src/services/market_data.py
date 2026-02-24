import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.models.models import OHLCV, Symbol
import logging

logger = logging.getLogger(__name__)

class MarketDataService:
    def __init__(self, db: Session):
        self.db = db

    def fetch_and_store(self, ticker: str, period: str = "1y", interval: str = "1d"):
        """
        Fetches data from Yahoo Finance and stores it in the database.
        Identifies latest saved date and only fetches new data (Delta).
        """
        logger.info(f"Fetching data for {ticker}...")

        # Get or create Symbol
        symbol = self.db.query(Symbol).filter(Symbol.ticker == ticker).first()
        if not symbol:
            symbol = Symbol(ticker=ticker)
            self.db.add(symbol)
            self.db.commit()
            self.db.refresh(symbol)

        # 1. Check for last timestamp
        last_record = self.db.query(OHLCV).filter(OHLCV.symbol_id == symbol.id).order_by(OHLCV.timestamp.desc()).first()

        start_date = None
        is_delta = False

        if last_record:
            # We have data - check if we need to fetch more
            last_date = last_record.timestamp
            today = datetime.now().date()
            
            # Count total records for this symbol
            total_records = self.db.query(OHLCV).filter(OHLCV.symbol_id == symbol.id).count()
            
            # If we have less than 200 days of data, fetch full history
            if total_records < 200:
                logger.info(f"{ticker} has only {total_records} days. Fetching full history...")
                is_delta = False
            # If last record is from today AND we have enough history, just update today
            elif last_date.date() == today and total_records >= 200:
                logger.info(f"Updating today's data for {ticker} ({total_records} days in DB)...")
                self.db.delete(last_record)
                self.db.commit()
                start_date = last_date
                is_delta = True
            # If last record is from the past, fetch from next day
            elif last_date.date() < today:
                start_date = last_date + timedelta(days=1)
                is_delta = True
                logger.info(f"Fetching delta data for {ticker} from {start_date.date()}...")
            else:
                # Already up to date
                logger.info(f"{ticker} is already up to date (Last: {last_date.date()})")
                return
        else:
            # No data exists - fetch full history
            logger.info(f"No existing data for {ticker}. Fetching full {period} history...")

        # 2. Fetch Data
        try:
            if is_delta:
                # yfinance expects string YYYY-MM-DD
                df = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), interval=interval, progress=False)
            else:
                # Initial Load
                df = yf.download(ticker, period=period, interval=interval, progress=False)

            if df.empty:
                logger.warning(f"No new data found for {ticker}")
                return

            # Optimization: Get all existing timestamps for this symbol at once
            existing_timestamps = set(
                ts[0] for ts in self.db.query(OHLCV.timestamp)
                .filter(OHLCV.symbol_id == symbol.id)
                .all()
            )

            new_records = 0
            for index, row in df.iterrows():
                # index is Timestamp
                ts = index.to_pydatetime()

                # Check if timestamp already exists (fast set lookup)
                if ts in existing_timestamps:
                    continue

                # Store new record
                try:
                    ohlcv = OHLCV(
                        symbol_id=symbol.id,
                        timestamp=ts,
                        open=float(row['Open'].iloc[0]) if hasattr(row['Open'], 'iloc') else float(row['Open']),
                        high=float(row['High'].iloc[0]) if hasattr(row['High'], 'iloc') else float(row['High']),
                        low=float(row['Low'].iloc[0]) if hasattr(row['Low'], 'iloc') else float(row['Low']),
                        close=float(row['Close'].iloc[0]) if hasattr(row['Close'], 'iloc') else float(row['Close']),
                        volume=float(row['Volume'].iloc[0]) if hasattr(row['Volume'], 'iloc') else float(row['Volume'])
                    )
                    self.db.add(ohlcv)
                    new_records += 1
                except Exception as e:
                    logger.error(f"Error storing record for {ticker} at {ts}: {e}")
                    continue

            self.db.commit()
            if new_records > 0:
                logger.info(f"Stored {new_records} new records for {ticker}")
            else:
                logger.info(f"No new records to store for {ticker}")

        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            self.db.rollback()

    def fetch_latest_news(self, ticker: str):
        """
        Fetches the latest news headline and link for the ticker.
        Returns a tuple (headline, url) or (None, None).
        """
        try:
            t = yf.Ticker(ticker)
            news = t.news
            if news:
                # Based on the structure observed: news[0]['content']['title']
                latest = news[0]
                content = latest.get('content', {})
                headline = content.get('title')

                # Try to get URL from clickThroughUrl or canonicalUrl
                url_obj = content.get('clickThroughUrl') or content.get('canonicalUrl')
                link = url_obj.get('url') if url_obj else None

                return headline, link
        except Exception as e:
            logger.error(f"Error fetching news for {ticker}: {e}")

        except Exception as e:
            logger.error(f"Error fetching news for {ticker}: {e}")

        return None, None

    def fetch_corporate_actions(self, ticker: str):
        """
        Fetches upcoming corporate actions (Dividends, Earnings) from calendar.
        Returns a dictionary of actions.
        """
        actions = {}
        try:
            t = yf.Ticker(ticker)
            cal = t.calendar
            if cal:
                # Calendar returns a dict where keys are event names and values are dates/lists
                # Example: {'Ex-Dividend Date': datetime.date(2025, 8, 14), 'Earnings Date': [datetime.date(...)]}

                ex_div = cal.get('Ex-Dividend Date')
                if ex_div:
                    actions['Ex-Dividend'] = ex_div

                earnings = cal.get('Earnings Date')
                if earnings:
                    # Earnings Date is often a list
                    if isinstance(earnings, list):
                        actions['Earnings'] = earnings[0]
                    else:
                        actions['Earnings'] = earnings

        except Exception as e:
            logger.error(f"Error fetching corporate actions for {ticker}: {e}")

    def fetch_shareholding_data(self, ticker: str):
        """
        Fetches shareholding data: Major Holders, Institutional Holders, Mutual Fund Holders.
        Returns a dictionary with dataframes or None.
        """
        data = {
            "major_holders": None,
            "institutional_holders": None,
            "mutual_fund_holders": None
        }
        try:
            t = yf.Ticker(ticker)

            # 1. Major Holders
            try:
                # yfinance returns a DataFrame
                data["major_holders"] = t.major_holders
            except Exception:
                pass

            # 2. Institutional Holders
            try:
                data["institutional_holders"] = t.institutional_holders
            except Exception:
                pass

            # 3. Mutual Fund Holders
            try:
                data["mutualfund_holders"] = t.mutualfund_holders
            except Exception:
                pass

        except Exception as e:
            logger.error(f"Error fetching shareholding for {ticker}: {e}")

        return data

    def fetch_insider_trading(self, ticker: str):
        """
        Fetches recent insider transactions.
        Returns a DataFrame or None.
        """
        try:
            t = yf.Ticker(ticker)
            return t.insider_transactions
        except Exception as e:
            logger.error(f"Error fetching insider transactions for {ticker}: {e}")
            return None
