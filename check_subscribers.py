from src.database.db import db_instance
from src.models.models import Subscriber
from dotenv import load_dotenv
import os

load_dotenv()

def check_subscribers():
    db = db_instance.SessionLocal()
    try:
        subscribers = db.query(Subscriber).all()
        print(f"Total Subscribers: {len(subscribers)}")
        for s in subscribers:
            print(f"ID: {s.id} | Chat ID: {s.chat_id} | Active: {s.is_active}")
            
        buy_id = os.getenv("TELEGRAM_BUY_CHANNEL_ID")
        sell_id = os.getenv("TELEGRAM_SELL_CHANNEL_ID")
        
        print(f"\nConfigured Buy Channel: {buy_id}")
        print(f"Configured Sell Channel: {sell_id}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_subscribers()
