from src.services.alerting import AlertService
from src.config.settings import Config
import logging

# Configure logger to see output
logging.basicConfig(level=logging.INFO)

def verify_routing():
    print("--- Verifying Alert Routing ---")
    service = AlertService()
    
    buy_id = Config.TELEGRAM_BUY_CHANNEL_ID
    sell_id = Config.TELEGRAM_SELL_CHANNEL_ID
    
    print(f"Buy Channel: {buy_id}")
    print(f"Sell Channel: {sell_id}")
    
    # 1. Send to Buy Channel ONLY
    print("\nSending 'Exclusive Buy Alert'...")
    service.send_telegram_message("✅ Exclusive Buy Alert - Should ONLY appear in Buy Channel", specific_chat_id=buy_id)
    
    # 2. Send to Sell Channel ONLY
    print("\nSending 'Exclusive Sell Alert'...")
    service.send_telegram_message("🔴 Exclusive Sell Alert - Should ONLY appear in Sell Channel", specific_chat_id=sell_id)
    
    print("\nDone. Please check your channels.")

if __name__ == "__main__":
    verify_routing()
