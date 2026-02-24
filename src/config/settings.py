import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/market_db")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    TELEGRAM_BUY_CHANNEL_ID = os.getenv("TELEGRAM_BUY_CHANNEL_ID")
    TELEGRAM_SELL_CHANNEL_ID = os.getenv("TELEGRAM_SELL_CHANNEL_ID")
    TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @staticmethod
    def _get_optional_float(key: str, default: str) -> Optional[float]:
        """Get float value or None if set to 'NA'"""
        value = os.getenv(key, default)
        if value.upper() == "NA":
            return None
        return float(value)

    @staticmethod
    def _get_optional_int(key: str, default: str) -> Optional[int]:
        """Get int value or None if set to 'NA'"""
        value = os.getenv(key, default)
        if value.upper() == "NA":
            return None
        return int(value)

    # RSI Strategy Parameters (Set to NA to skip filter)
    RSI_OVERSOLD_THRESHOLD = _get_optional_float.__func__("RSI_OVERSOLD_THRESHOLD", "30")
    RSI_OVERBOUGHT_THRESHOLD = _get_optional_float.__func__("RSI_OVERBOUGHT_THRESHOLD", "70")
    RSI_RISING_CANDLES = _get_optional_int.__func__("RSI_RISING_CANDLES", "2")
    RSI_FALLING_CANDLES = _get_optional_int.__func__("RSI_FALLING_CANDLES", "2")

    # Heikin Ashi Strategy Parameters (Set to NA to skip filter)
    HA_CONSECUTIVE_CANDLES = _get_optional_int.__func__("HA_CONSECUTIVE_CANDLES", "2")

    # Trend Damage Check Parameters (Set to NA to skip filter)
    MAX_DISTANCE_BELOW_SMA200_PERCENT = _get_optional_float.__func__("MAX_DISTANCE_BELOW_SMA200_PERCENT", "18")

    # Volume Strategy Parameters (Set to NA to skip filter)
    VOLUME_MULTIPLIER = _get_optional_float.__func__("VOLUME_MULTIPLIER", "1.2")
    VOLUME_AVERAGE_PERIOD = int(os.getenv("VOLUME_AVERAGE_PERIOD", "20"))

    # Dual Window Strategy Parameters
    DATA_LOOKBACK_DAYS = int(os.getenv("DATA_LOOKBACK_DAYS", "365"))
    PRIMARY_WINDOW_CANDLES = int(os.getenv("PRIMARY_WINDOW_CANDLES", "70"))
    CONFIRMATION_WINDOW_CANDLES = int(os.getenv("CONFIRMATION_WINDOW_CANDLES", "30"))

    # Market Cap Filter Parameters (Set to NA to skip filter)
    MIN_MARKET_CAP_CRORE = _get_optional_float.__func__("MIN_MARKET_CAP_CRORE", "10000")
