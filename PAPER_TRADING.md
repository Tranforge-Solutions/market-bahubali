# Paper Trading Module - Channel Integration

## Overview
This module enables simulated trade execution via Telegram **channels**, allowing users to validate the trading strategy without real capital risk.

## How It Works with Channels

### Signal Flow:
1. **Signal Posted to Channel**: Trading signal sent to BUY/SELL channel
2. **BUY Button with Deep Link**: Button opens private chat with bot
3. **Private Chat Execution**: User completes trade in private bot chat
4. **Trade Tracking**: All trades tracked per user in database

### Why Deep Links?
- Channels don't support interactive callbacks for all users
- Deep links redirect users to private bot chat
- Each user gets isolated trade management
- SELL buttons only shown for user's own trades

## User Flow

1. **User sees signal in channel**
   - Signal posted to @YourBuyChannel or @YourSellChannel
   - BUY button visible to all channel members

2. **User clicks BUY button**
   - Opens private chat with bot
   - Bot shows: "Quick Buy" or "Configure Order"

3. **User confirms trade**
   - Trade created with status: OPEN
   - User receives confirmation with trade details

4. **User manages trades**
   - `/mytrades` - View all open trades
   - SELL button shown for each open trade
   - Click SELL to close trade

## Bot Commands

- `/start` - Subscribe to paper trading
- `/mytrades` - View your open trades with SELL buttons

## Setup

### 1. Create Telegram Bot
```
1. Talk to @BotFather on Telegram
2. Create new bot: /newbot
3. Get bot token and username
4. Add to .env:
   TELEGRAM_BOT_TOKEN=your_token
   TELEGRAM_BOT_USERNAME=your_bot_username
```

### 2. Configure Channels (Use Existing)
```
You already have channels configured:
- TELEGRAM_BUY_CHANNEL_ID=-1003768414047
- TELEGRAM_SELL_CHANNEL_ID=-1003553292633

Just add your bot:
1. Add bot as admin to both existing channels
2. Bot will post signals with BUY buttons there
3. Users click BUY → opens private chat with bot
```

## Features
- ✅ Interactive BUY/SELL buttons in Telegram
- ✅ Paper trade execution and tracking
- ✅ Stop Loss & Target management
- ✅ Auto-exit monitoring
- ✅ P&L calculation and analytics
- ✅ Per-user trade isolation
- ✅ Strategy performance metrics

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Telegram Bot (Separate Process)
```bash
python run_bot.py
```

### 3. Run API Server
```bash
uvicorn src.api:app --reload
```

## User Flow

1. **Subscribe**: User sends `/start` to bot
2. **Receive Signal**: Bot sends trading signal with BUY button
3. **Place Trade**: User clicks BUY → chooses Quick Buy or Configure
4. **Monitor**: Trade tracked in database with OPEN status
5. **Exit**: User clicks SELL button or auto-exit triggers
6. **Analyze**: View P&L and performance stats

## API Endpoints

### Get Paper Trades
```
GET /paper-trades?status=OPEN&limit=50
```

### Get Statistics
```
GET /paper-trades/stats
```

Returns:
- Total trades
- Open/Closed counts
- Win rate
- Average P&L

## Database Schema

### PaperTrade Table
- `subscriber_id`: User reference
- `signal_id`: Signal reference
- `entry_price`, `exit_price`: Execution prices
- `quantity`: Trade size
- `stop_loss`, `target_price`: Risk management
- `auto_exit`: Auto-exit enabled flag
- `status`: OPEN, CLOSED, EXPIRED
- `pnl`, `pnl_percent`: Profit/Loss metrics

## Disclaimer
⚠️ **This is a simulated trading environment for testing and educational purposes. No real trades are executed.**

## Future Enhancements
- Partial exit support
- Advanced order types (Limit, Stop)
- Broker integration (Zerodha)
- Live/Paper mode toggle
