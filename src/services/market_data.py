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
            # We have data
            last_date = last_record.timestamp
            today = datetime.now().date()
            
            # If last record is from today, it might be incomplete/stale.
            # We should delete it and re-fetch to get the latest close/volume.
            if last_date.date() == today:
                logger.info(f"Existing data for today ({today}) found. Removing to refresh...")
                self.db.delete(last_record)
                self.db.commit()
                # Set start_date to today to re-fetch
                start_date = last_date
            else:
                # Last record is from the past. Fetch from next day.
                start_date = last_date + timedelta(days=1)
                
                # Check if we are already up to date (Start Date > Today)
                if start_date.date() > today:
                    logger.info(f"{ticker} is already up to date (Last: {last_date.date()})")
                    return

            is_delta = True
            logger.info(f"Fetching data for {ticker} from {start_date.date()}...")

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

            new_records = 0
            for index, row in df.iterrows():
                # index is Timestamp
                ts = index.to_pydatetime()
                
                # Double check existence (optimization: could skip this if confident in delta logic)
                exists = self.db.query(OHLCV).filter(
                    OHLCV.symbol_id == symbol.id,
                    OHLCV.timestamp == ts
                ).first()
                
                if not exists:
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
