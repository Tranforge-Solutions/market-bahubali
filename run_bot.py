#!/usr/bin/env python3
"""
Telegram Bot Runner for Paper Trading
Run this separately to handle interactive Telegram callbacks
"""
import logging
from dotenv import load_dotenv
from src.services.telegram_bot import TelegramBotHandler
from src.database.db import db_instance

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    load_dotenv()
    
    # Initialize database
    db_instance.create_tables()
    logger.info("Database initialized.")
    
    # Start bot
    logger.info("Starting Telegram Bot...")
    bot = TelegramBotHandler()
    bot.run()

if __name__ == "__main__":
    main()
