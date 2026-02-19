import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/market_db")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    TELEGRAM_BUY_CHANNEL_ID = os.getenv("TELEGRAM_BUY_CHANNEL_ID")
    TELEGRAM_SELL_CHANNEL_ID = os.getenv("TELEGRAM_SELL_CHANNEL_ID")
    TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # RSI Strategy Parameters
    RSI_OVERSOLD_THRESHOLD = float(os.getenv("RSI_OVERSOLD_THRESHOLD", "30"))
    RSI_OVERBOUGHT_THRESHOLD = float(os.getenv("RSI_OVERBOUGHT_THRESHOLD", "70"))
    RSI_RISING_CANDLES = int(os.getenv("RSI_RISING_CANDLES", "2"))
    RSI_FALLING_CANDLES = int(os.getenv("RSI_FALLING_CANDLES", "2"))

    # Heikin Ashi Strategy Parameters
    HA_CONSECUTIVE_CANDLES = int(os.getenv("HA_CONSECUTIVE_CANDLES", "2"))

    # Trend Damage Check Parameters
    MAX_DISTANCE_BELOW_SMA200_PERCENT = float(os.getenv("MAX_DISTANCE_BELOW_SMA200_PERCENT", "18"))

    # Volume Strategy Parameters
    VOLUME_MULTIPLIER = float(os.getenv("VOLUME_MULTIPLIER", "1.2"))
    VOLUME_AVERAGE_PERIOD = int(os.getenv("VOLUME_AVERAGE_PERIOD", "20"))

    # Dual Window Strategy Parameters
    DATA_LOOKBACK_DAYS = int(os.getenv("DATA_LOOKBACK_DAYS", "365"))
    PRIMARY_WINDOW_CANDLES = int(os.getenv("PRIMARY_WINDOW_CANDLES", "70"))
    CONFIRMATION_WINDOW_CANDLES = int(os.getenv("CONFIRMATION_WINDOW_CANDLES", "30"))

    # Market Cap Filter Parameters
    MIN_MARKET_CAP_CRORE = float(os.getenv("MIN_MARKET_CAP_CRORE", "10000"))
