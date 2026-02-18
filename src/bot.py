import time
import requests
import json
import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from dotenv import load_dotenv
from src.database.db import db_instance, Base
from src.models.models import Order, Symbol, Subscriber
from src.services.alerting import AlertService

# Helper to send simple text
def send_telegram_message(chat_id, text):
    import requests
    import os
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

# Setup
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TradingBot")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/"

# Database Initialization
db_instance.create_tables() # Use shared instance to create tables

# User State
user_state = {}

def get_updates(offset=None):
    url = f"{BASE_URL}getUpdates"
    params = {"timeout": 60, "offset": offset}
    try:
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        logger.error(f"Error getting updates: {e}")
        return None

def send_message(chat_id, text):
    url = f"{BASE_URL}sendMessage"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)

def save_order(ticker, action, price, qty):
    db = db_instance.SessionLocal()
    try:
        # Find symbol ID
        symbol = db.query(Symbol).filter(Symbol.ticker == ticker).first()
        if not symbol:
             symbol = Symbol(ticker=ticker)
             db.add(symbol)
             db.commit()
             db.refresh(symbol)
             
        order = Order(symbol_id=symbol.id, action=action, price=price, quantity=qty, status="EXECUTED")
        db.add(order)
        db.commit()
        return True, order.id
    except Exception as e:
        logger.error(f"DB Error: {e}")
        return False, None
    finally:
        db.close()

def handle_callback(update):
    query = update['callback_query']
    user_id = query['from']['id']
    data = query['data']
    chat_id = query['message']['chat']['id']
    
    # Acknowledge callback (stop spinner)
    requests.post(f"{BASE_URL}answerCallbackQuery", data={"callback_query_id": query['id']})
    
    if data.startswith("BUY:"):
        # Format: BUY:RELIANCE.NS:1456.80
        parts = data.split(":")
        ticker = parts[1]
        price = float(parts[2])
        
        user_state[user_id] = {
            "step": "WAITING_QTY",
            "ticker": ticker,
            "action": "BUY",
            "price": price
        }
        
        send_message(chat_id, f"⚡ Initiating BUY for {ticker} @ ₹{price}\n\n🔢 Please enter the QUANTITY:")

def handle_message(update):
    msg = update.get('message')
    if not msg or 'text' not in msg:
        return

    user_id = msg['from']['id']
    chat_id = str(msg['chat']['id'])
    text = msg.get('text', '')
    
    if text == '/start':
        try:
            db = db_instance.SessionLocal()
            existing = db.query(Subscriber).filter(Subscriber.chat_id == chat_id).first()
            if not existing:
                new_sub = Subscriber(chat_id=chat_id)
                db.add(new_sub)
                db.commit()
                welcome_msg = "Welcome! 🚀\nYou are now subscribed to Market Alerts."
            else:
                if not existing.is_active:
                    existing.is_active = True
                    db.commit()
                    welcome_msg = "Welcome Back! 🔄\nYou are re-subscribed."
                else:
                    welcome_msg = "You are already subscribed! ✅"
            
            db.close()
            send_telegram_message(chat_id, welcome_msg)
        except Exception as e:
            logger.error(f"Subscription error: {e}")
            send_message(chat_id, "Error processing subscription.")
        return

    # Handle numeric input for Order Quantity
    state = user_state.get(user_id)
    
    if state and state['step'] == "WAITING_QTY":
        try:
            qty = int(text)
            if qty <= 0:
                send_message(chat_id, "❌ Quantity must be positive. Try again:")
                return
                
            # Execute Order
            success, order_id = save_order(state['ticker'], state['action'], state['price'], qty)
            
            if success:
                send_message(chat_id, f"✅ <b>Order Placed Successfully!</b>\n"
                                      f"🆔 ID: #{order_id}\n"
                                      f"💎 Stock: {state['ticker']}\n"
                                      f"📊 Qty: {qty}\n"
                                      f"💰 Value: ₹{qty * state['price']:.2f}")
            else:
                send_message(chat_id, "❌ Failed to save order. Database error.")
            
            # Clear state
            del user_state[user_id]
            
        except ValueError:
            send_message(chat_id, "❌ Invalid quantity. Please enter a valid number (e.g., 10, 50).")
    else:
        # Default response for unhandled text
        send_message(chat_id, "🤖 Market Monitor Bot is Active! Wait for alerts.")

def main():
    logger.info("Bot started. Listening for updates...")
    print("Bot is running...")
    
    last_update_id = None
    
    while True:
        updates = get_updates(last_update_id)
        
        if updates and updates.get('ok'):
            for update in updates['result']:
                last_update_id = update['update_id'] + 1
                
                if 'callback_query' in update:
                    handle_callback(update)
                elif 'message' in update:
                    handle_message(update)
        
        time.sleep(1)

if __name__ == "__main__":
    main()
