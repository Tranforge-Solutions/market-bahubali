import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    print("Error: TELEGRAM_BOT_TOKEN not found in .env")
    exit(1)

url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
print(f"Checking for updates...")

try:
    response = requests.get(url)
    data = response.json()
    
    if not data.get("ok"):
        print(f"Error: {data}")
        exit(1)
        
    results = data.get("result", [])
    if not results:
        print("\nNo updates found. Make sure you have:")
        print("1. Created the channel.")
        print("2. Added the bot as an Administrator.")
        print("3. Sent a message (e.g. 'hello') in the channel.")
    else:
        print(f"\nFound {len(results)} updates. Looking for channels...\n")
        found_channels = set()
        for update in results:
            if 'channel_post' in update:
                chat = update['channel_post']['chat']
                chat_id = chat['id']
                title = chat['title']
                if chat_id not in found_channels:
                    print(f"✅ Found Channel: '{title}' | ID: {chat_id}")
                    found_channels.add(chat_id)
            elif 'message' in update:
                chat = update['message']['chat']
                if chat['type'] == 'channel':
                     print(f"✅ Found Channel: '{chat['title']}' | ID: {chat['id']}")
        
        if not found_channels:
            print("No channel messages found in the updates.")
            print("Please send a message in your channel and try again.")

except Exception as e:
    print(f"Error: {e}")
