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
