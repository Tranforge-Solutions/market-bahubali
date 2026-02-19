import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/market_db")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    TELEGRAM_BUY_CHANNEL_ID = os.getenv("TELEGRAM_BUY_CHANNEL_ID")
    TELEGRAM_SELL_CHANNEL_ID = os.getenv("TELEGRAM_SELL_CHANNEL_ID")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # RSI Strategy Parameters
    RSI_OVERSOLD_THRESHOLD = float(os.getenv("RSI_OVERSOLD_THRESHOLD", "30"))
    RSI_OVERBOUGHT_THRESHOLD = float(os.getenv("RSI_OVERBOUGHT_THRESHOLD", "70"))
    RSI_RISING_CANDLES = int(os.getenv("RSI_RISING_CANDLES", "2"))
    RSI_FALLING_CANDLES = int(os.getenv("RSI_FALLING_CANDLES", "2"))
