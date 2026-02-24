import pandas as pd
from sqlalchemy.orm import Session
from src.models.models import OHLCV, Symbol

class IndicatorService:
    def __init__(self, db: Session):
        self.db = db

    def load_data(self, ticker: str, lookback_days: int = None) -> pd.DataFrame:
        """Loads OHLCV data from DB into a Pandas DataFrame."""
        from src.config.settings import Config
        from datetime import datetime, timedelta
        import pytz

        if lookback_days is None:
            lookback_days = Config.DATA_LOOKBACK_DAYS

        symbol = self.db.query(Symbol).filter(Symbol.ticker == ticker).first()
        if not symbol:
            return pd.DataFrame()

        # Calculate cutoff date with UTC timezone to match DB timestamps
        cutoff_date = datetime.now(pytz.UTC) - timedelta(days=lookback_days)

        # Query data with lookback limit
        data = self.db.query(OHLCV).filter(
            OHLCV.symbol_id == symbol.id,
            OHLCV.timestamp >= cutoff_date
        ).order_by(OHLCV.timestamp.asc()).all()

        if not data:
            return pd.DataFrame()

        records = [{
            'timestamp': d.timestamp,
            'open': d.open,
            'high': d.high,
            'low': d.low,
            'close': d.close,
            'volume': d.volume
        } for d in data]

        df = pd.DataFrame(records)
        df.set_index('timestamp', inplace=True)
        
        # Debug: Log dataframe size
        if len(df) < 200:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Loaded only {len(df)} days for {ticker} (expected 200+)")
        
        return df

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies TA indicators to the DataFrame using standard Pandas."""
        if df.empty:
            return df

        # Helper for SMA
        def calculate_sma(series, window):
            return series.rolling(window=window).mean()

        # Helper for RSI
        def calculate_rsi(series, window=14):
            delta = series.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))

        # Helper for ATR
        def calculate_atr(df, window=14):
            high_low = df['high'] - df['low']
            high_close = (df['high'] - df['close'].shift()).abs()
            low_close = (df['low'] - df['close'].shift()).abs()
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            return tr.rolling(window=window).mean()

        # Helper for Heikin Ashi
        def calculate_heikin_ashi(df):
            ha_close = (df['open'] + df['high'] + df['low'] + df['close']) / 4
            ha_open = [df['open'].iloc[0]] # Initialize with first real open

            # Iterative calculation for HA Open
            # HA_Open = (Prev HA_Open + Prev HA_Close) / 2
            for i in range(1, len(df)):
                prev_open = ha_open[-1]
                prev_close = ha_close.iloc[i-1]
                ha_open.append((prev_open + prev_close) / 2)

            df['HA_Close'] = ha_close
            df['HA_Open'] = ha_open
            df['HA_High'] = df[['high', 'HA_Open', 'HA_Close']].max(axis=1)
            df['HA_Low'] = df[['low', 'HA_Open', 'HA_Close']].min(axis=1)

            # Determine Color (True for Green/Bullish, False for Red/Bearish)
            df['HA_Green'] = df['HA_Close'] > df['HA_Open']
            return df

        # SMAs
        df['SMA_20'] = calculate_sma(df['close'], 20)
        df['SMA_50'] = calculate_sma(df['close'], 50)
        df['SMA_200'] = calculate_sma(df['close'], 200)

        # RSI
        df['RSI'] = calculate_rsi(df['close'], 14)

        # ATR
        df['ATR'] = calculate_atr(df, 14)

        # Heikin Ashi
        df = calculate_heikin_ashi(df)

        # Volume Z-Score (Custom calculation)
        # Z = (Vol - Mean) / StdDev over 30 days
        roll = df['volume'].rolling(window=30)
        df['Vol_Mean'] = roll.mean()
        df['Vol_Std'] = roll.std()
        df['Vol_Z'] = (df['volume'] - df['Vol_Mean']) / df['Vol_Std']

        # Fill NaN for initial periods if needed, or leave as is (Scoring handles NaNs implicitly by false conditions)
        return df
