import requests
import logging
from src.config.settings import Config

logger = logging.getLogger(__name__)

class AlertService:
    def __init__(self):
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID
        self.buy_channel_id = Config.TELEGRAM_BUY_CHANNEL_ID
        self.sell_channel_id = Config.TELEGRAM_SELL_CHANNEL_ID

    def send_telegram_message(self, message: str, specific_chat_id=None):
        """Sends a message to the configured Telegram chat or a specific chat ID."""
        if not self.bot_token:
            logger.warning("Telegram bot token missing. Skipping alert.")
            return

        # If specific_chat_id is provided, verify it. Otherwise fallback to default.
        target_chat_id = specific_chat_id if specific_chat_id else self.chat_id
        
        if not target_chat_id:
            logger.warning("No target chat ID provided.")
            return

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": target_chat_id,
            "text": message,
            "parse_mode": "HTML"
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            logger.info(f"Telegram alert sent successfully to {target_chat_id}.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Telegram alert: {e}")

    def send_telegram_photo(self, caption: str, photo, buttons=None, specific_chat_id=None):
        """
        Sends a photo with a caption to all subscribed Telegram users and optionally a specific channel.
        photo: Can be a file path (str) or a file-like object (BytesIO).
        buttons: List of inline buttons (optional).
        # specific_chat_id: Optional channel ID to send to INSTEAD of subscribers (for targeted campaigns)
        """
        import json
        from src.database.db import db_instance
        from src.models.models import Subscriber
        
        chat_ids = []
        
        # If specific_chat_id is provided, use it as priority
        if specific_chat_id:
            chat_ids.append(specific_chat_id)
            logger.info(f"Sending to specific channel: {specific_chat_id}")
        else:
            # Otherwise, get Subscribers from database
            db = db_instance.SessionLocal()
            try:
                subscribers = db.query(Subscriber).filter(Subscriber.is_active == True).all()
                chat_ids = [s.chat_id for s in subscribers]
                logger.info(f"Found {len(chat_ids)} subscribers")
            except Exception as e:
                logger.error(f"Error fetching subscribers: {e}")
            finally:
                db.close()
            
            # Fallback to default chat_id if list is empty
            if not chat_ids and self.chat_id:
                chat_ids.append(self.chat_id)
                logger.info(f"Using default chat_id: {self.chat_id}")

        if not chat_ids:
            logger.warning("No recipients found. Skipping alert.")
            return
            
        # Prepare Payload
        base_payload = {
            "caption": caption,
            "parse_mode": "HTML"
        }
        
        if buttons:
            if isinstance(buttons, dict):
                 base_payload['reply_markup'] = json.dumps(buttons)
            else:
                 base_payload['reply_markup'] = json.dumps({"inline_keyboard": buttons})

        # Construct URL
        base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # Broadcast
        for chat_id in set(chat_ids):
            try:
                payload = base_payload.copy()
                payload['chat_id'] = chat_id
                
                # Handle Photo (Reset stream if needed)
                if hasattr(photo, 'read'):
                    photo.seek(0)
                    files = {'photo': photo}
                else: 
                     files = {'photo': open(photo, 'rb')} if isinstance(photo, str) else None
                     
                resp = requests.post(f"{base_url}/sendPhoto", data=payload, files=files)
                if resp.ok:
                    logger.info(f"Alert sent successfully to {chat_id}")
                else:
                    logger.error(f"Failed to send to {chat_id}: {resp.text}")
                    
            except Exception as e:
                logger.error(f"Broadcast error to {chat_id}: {e}")
