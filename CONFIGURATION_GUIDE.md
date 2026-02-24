# Market Monitoring System - Configuration Guide

## 📋 Overview
This guide explains how to configure the Market Monitoring System without any coding knowledge. You only need basic business understanding of stock trading concepts.

---

## 🔧 Configuration File (.env)

All settings are controlled through environment variables. Each setting controls how the system filters and selects stocks.

---

## 📊 STOCK FILTERING PROCESS (Step-by-Step)

The system filters stocks through multiple stages. Each stage eliminates stocks that don't meet the criteria:

```
All Stocks (Nifty 500)
    ↓
[FILTER 1] Market Cap Filter
    ↓
[FILTER 2] Data Quality Check
    ↓
[FILTER 3] RSI Analysis
    ↓
[FILTER 4] Heikin Ashi Trend
    ↓
[FILTER 5] Volume Confirmation
    ↓
[FILTER 6] Trend Damage Check
    ↓
[FILTER 7] Dual Window Scoring
    ↓
Final Buy/Sell Signals → Telegram Alert
```

---

## 🔐 SECTION 1: Database & Telegram Configuration

### DATABASE_URL
**What it does:** Connection string to your PostgreSQL database  
**Who sets it:** Automatically provided by Render.com  
**Example:** `postgresql://user:password@host:5432/database`  
**Don't change this manually**

### TELEGRAM_BOT_TOKEN
**What it does:** Authenticates your Telegram bot  
**How to get:**
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow instructions to create bot
4. Copy the token provided

**Example:** `8340769586:AAFgWHHvlKQBdEFFlQ3mmsSVDo9TP_P_jeY`

### TELEGRAM_CHAT_ID
**What it does:** Your personal Telegram user ID for admin notifications  
**How to get:**
1. Search for `@userinfobot` on Telegram
2. Start chat and it will show your ID

**Example:** `6682705633`

### TELEGRAM_BUY_CHANNEL_ID
**What it does:** Channel where BUY signals are posted  
**How to get:**
1. Create a Telegram channel
2. Add your bot as admin
3. Forward any message from channel to `@userinfobot`
4. Copy the channel ID (includes negative sign)

**Example:** `-1003768414047`  
**Important:** Keep the negative sign (-)

### TELEGRAM_SELL_CHANNEL_ID
**What it does:** Channel where SELL signals are posted  
**Same process as BUY channel**

**Example:** `-1003553292633`

### TELEGRAM_BOT_USERNAME
**What it does:** Your bot's username (for reference only)  
**Example:** `Market_bahubali_bot`

---

## 📈 SECTION 2: Stock Filtering Rules

### FILTER 1: Market Cap Filter

#### MIN_MARKET_CAP_CRORE
**What it does:** Only scan stocks with market cap above this value  
**Purpose:** Filter out small, risky companies  
**Default:** `10000` (₹10,000 Crores)

**Business Logic:**
- Higher value = Only large, stable companies (safer but fewer signals)
- Lower value = Include mid-cap companies (more signals but riskier)

**Recommended Values:**
- Conservative: `50000` (Large cap only)
- Balanced: `10000` (Large + Mid cap)
- Aggressive: `5000` (Include smaller mid-caps)

---

### FILTER 2: Data Lookback Period

#### DATA_LOOKBACK_DAYS
**What it does:** How many days of historical data to analyze  
**Default:** `365` (1 year)

**Business Logic:**
- More days = Better trend analysis but slower processing
- Fewer days = Faster but may miss long-term patterns

**Recommended Values:**
- Short-term trading: `180` (6 months)
- Medium-term: `365` (1 year)
- Long-term: `730` (2 years)

---

### FILTER 3: RSI (Relative Strength Index) Strategy

RSI measures if a stock is "oversold" (cheap) or "overbought" (expensive) on a scale of 0-100.

#### RSI_OVERSOLD_THRESHOLD
**What it does:** Below this value = Stock is oversold (potential BUY)  
**Default:** `30`

**Business Logic:**
- Lower value (20-25) = Very strict, only extreme dips (fewer but stronger signals)
- Higher value (35-40) = More relaxed, catch earlier (more signals but weaker)

**Recommended Values:**
- Conservative: `25` (Wait for deep dips)
- Balanced: `30` (Standard)
- Aggressive: `35` (Early entry)

#### RSI_OVERBOUGHT_THRESHOLD
**What it does:** Above this value = Stock is overbought (potential SELL)  
**Default:** `70`

**Business Logic:**
- Higher value (75-80) = Very strict, only extreme peaks (fewer signals)
- Lower value (65-70) = More relaxed, catch earlier (more signals)

**Recommended Values:**
- Conservative: `75` (Wait for peak)
- Balanced: `70` (Standard)
- Aggressive: `65` (Early exit)

#### RSI_RISING_CANDLES
**What it does:** How many consecutive candles RSI must rise for BUY confirmation  
**Default:** `2`

**Business Logic:**
- More candles = Stronger confirmation but delayed entry
- Fewer candles = Faster entry but more false signals

**Recommended Values:**
- Quick entry: `1`
- Balanced: `2`
- Safe entry: `3`

#### RSI_FALLING_CANDLES
**What it does:** How many consecutive candles RSI must fall for SELL confirmation  
**Default:** `2`

**Same logic as RSI_RISING_CANDLES**

---

### FILTER 4: Heikin Ashi Trend Confirmation

Heikin Ashi candles smooth out price action to identify trends clearly.

#### HA_CONSECUTIVE_CANDLES
**What it does:** How many consecutive green/red candles needed to confirm trend  
**Default:** `2`

**Business Logic:**
- More candles = Stronger trend confirmation but delayed signals
- Fewer candles = Faster signals but more noise

**Recommended Values:**
- Aggressive: `1` (Quick but risky)
- Balanced: `2` (Standard)
- Conservative: `3` (Strong confirmation)

---

### FILTER 5: Volume Confirmation

Volume confirms if the price movement has real buying/selling pressure.

#### VOLUME_MULTIPLIER
**What it does:** Current volume must be this many times higher than average  
**Default:** `1.2` (20% higher than average)

**Business Logic:**
- Higher multiplier (1.5-2.0) = Only strong volume spikes (fewer but quality signals)
- Lower multiplier (1.1-1.3) = Accept moderate volume (more signals)

**Recommended Values:**
- Strict: `1.5` (50% above average)
- Balanced: `1.2` (20% above average)
- Relaxed: `1.1` (10% above average)

#### VOLUME_AVERAGE_PERIOD
**What it does:** How many days to calculate average volume  
**Default:** `20` (20-day average)

**Business Logic:**
- Longer period (30-50) = Smoother average, less sensitive
- Shorter period (10-15) = More responsive to recent changes

**Recommended Values:**
- Standard: `20` (Industry standard)
- Responsive: `10` (Quick adaptation)
- Stable: `30` (Smooth average)

---

### FILTER 6: Trend Damage Check

Prevents buying stocks in severe downtrends.

#### MAX_DISTANCE_BELOW_SMA200_PERCENT
**What it does:** Maximum % a stock can be below its 200-day average  
**Default:** `18` (18% below 200-day SMA)

**Business Logic:**
- If stock is more than 18% below its 200-day average = Trend is damaged, skip it
- Lower value (10-15%) = Very strict, only healthy trends
- Higher value (20-25%) = More lenient, allow deeper corrections

**Recommended Values:**
- Strict: `12%` (Only strong uptrends)
- Balanced: `18%` (Standard)
- Lenient: `25%` (Allow deeper corrections)

---

### FILTER 7: Dual Window Scoring System

This is the final scoring mechanism that ranks stocks from 0-100.

#### PRIMARY_WINDOW_CANDLES
**What it does:** Number of recent candles for primary trend analysis  
**Default:** `70` (70 candles)

**Business Logic:**
- Larger window (80-100) = Focus on longer-term trends
- Smaller window (50-60) = More responsive to recent changes

**Recommended Values:**
- Long-term: `90`
- Balanced: `70`
- Short-term: `50`

#### CONFIRMATION_WINDOW_CANDLES
**What it does:** Number of very recent candles for immediate confirmation  
**Default:** `30` (30 candles)

**Business Logic:**
- Must be smaller than PRIMARY_WINDOW
- Larger value (40-50) = Broader confirmation
- Smaller value (20-30) = Focus on immediate action

**Recommended Values:**
- Broad: `40`
- Balanced: `30`
- Immediate: `20`

---

## 🎯 SCORING SYSTEM EXPLAINED

After all filters pass, stocks get a score from 0-100:

### Score Ranges:
- **80-100:** High Confidence (Strong signal)
- **60-79:** Medium Confidence (Good signal)
- **40-59:** Low Confidence (Weak signal)
- **0-39:** No Trade (Rejected)

### What Increases Score:
✅ RSI in oversold/overbought zone  
✅ Multiple consecutive Heikin Ashi candles  
✅ High volume confirmation  
✅ Price near support/resistance  
✅ Strong trend in both windows  

### What Decreases Score:
❌ Weak volume  
❌ Mixed signals  
❌ Trend damage  
❌ Conflicting indicators  

---

## 🎨 PRESET CONFIGURATIONS

### Conservative (Safe, Fewer Signals)
```
MIN_MARKET_CAP_CRORE=50000
RSI_OVERSOLD_THRESHOLD=25
RSI_OVERBOUGHT_THRESHOLD=75
HA_CONSECUTIVE_CANDLES=3
VOLUME_MULTIPLIER=1.5
MAX_DISTANCE_BELOW_SMA200_PERCENT=12
PRIMARY_WINDOW_CANDLES=90
CONFIRMATION_WINDOW_CANDLES=40
```

### Balanced (Recommended)
```
MIN_MARKET_CAP_CRORE=10000
RSI_OVERSOLD_THRESHOLD=30
RSI_OVERBOUGHT_THRESHOLD=70
HA_CONSECUTIVE_CANDLES=2
VOLUME_MULTIPLIER=1.2
MAX_DISTANCE_BELOW_SMA200_PERCENT=18
PRIMARY_WINDOW_CANDLES=70
CONFIRMATION_WINDOW_CANDLES=30
```

### Aggressive (More Signals, Higher Risk)
```
MIN_MARKET_CAP_CRORE=5000
RSI_OVERSOLD_THRESHOLD=35
RSI_OVERBOUGHT_THRESHOLD=65
HA_CONSECUTIVE_CANDLES=1
VOLUME_MULTIPLIER=1.1
MAX_DISTANCE_BELOW_SMA200_PERCENT=25
PRIMARY_WINDOW_CANDLES=50
CONFIRMATION_WINDOW_CANDLES=20
```

---

## 📝 HOW TO CHANGE SETTINGS

### On Render.com:
1. Go to your Render.com dashboard
2. Select your service
3. Click "Environment" tab
4. Click "Add Environment Variable"
5. Enter variable name and value
6. Click "Save Changes"
7. Service will automatically restart

### Testing Your Changes:
1. Trigger a manual scan: `POST /run-job`
2. Check job status: `GET /job-status`
3. Review signals: `GET /signals`
4. Monitor Telegram channels for alerts

---

## ⚠️ IMPORTANT WARNINGS

1. **Don't change DATABASE_URL** - It's auto-generated
2. **Keep negative signs** in Telegram channel IDs
3. **Test changes gradually** - Change one parameter at a time
4. **Monitor results** for 1-2 weeks before making more changes
5. **Backup settings** before major changes

---

## 🆘 TROUBLESHOOTING

### No signals generated?
- **Increase** RSI thresholds (30→35 for oversold, 70→65 for overbought)
- **Decrease** HA_CONSECUTIVE_CANDLES (3→2 or 2→1)
- **Decrease** VOLUME_MULTIPLIER (1.5→1.2)
- **Increase** MAX_DISTANCE_BELOW_SMA200_PERCENT (18→25)

### Too many false signals?
- **Decrease** RSI thresholds (35→30 for oversold, 65→70 for overbought)
- **Increase** HA_CONSECUTIVE_CANDLES (1→2 or 2→3)
- **Increase** VOLUME_MULTIPLIER (1.2→1.5)
- **Decrease** MAX_DISTANCE_BELOW_SMA200_PERCENT (25→18)

### Signals too late?
- **Decrease** RSI_RISING_CANDLES and RSI_FALLING_CANDLES
- **Decrease** HA_CONSECUTIVE_CANDLES
- **Decrease** PRIMARY_WINDOW_CANDLES

### Signals too early (risky)?
- **Increase** RSI_RISING_CANDLES and RSI_FALLING_CANDLES
- **Increase** HA_CONSECUTIVE_CANDLES
- **Increase** PRIMARY_WINDOW_CANDLES

---

## 📞 SUPPORT

For questions or issues:
- Check `/job-status` endpoint for errors
- Review Telegram alerts for signal quality
- Monitor `/signals` endpoint for historical performance

---

**Last Updated:** February 2026  
**Version:** 1.0
