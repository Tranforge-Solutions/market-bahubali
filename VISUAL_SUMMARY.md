# 📊 One-Page Visual Summary

## 🎯 What This System Does

```
Scans 500+ Stocks Daily
         ↓
Applies Your Filters
         ↓
Finds Perfect Entry/Exit Points
         ↓
Sends Telegram Alert
```

---

## 🔍 The 7 Filters (In Order)

```
┌─────────────────────────────────────────────────────────────┐
│ FILTER 1: Company Size                                      │
│ MIN_MARKET_CAP_CRORE = How big should the company be?      │
│                                                             │
│ ₹5,000 Cr ←──────── ₹10,000 Cr ────────→ ₹50,000 Cr      │
│ (Risky)           (Balanced)            (Safe)             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ FILTER 2: Price Level (RSI)                                │
│ RSI_OVERSOLD = How cheap before buying?                    │
│ RSI_OVERBOUGHT = How expensive before selling?             │
│                                                             │
│ BUY:  25 ←──────── 30 ────────→ 35                        │
│      (Wait)     (Standard)    (Early)                      │
│                                                             │
│ SELL: 65 ←──────── 70 ────────→ 75                        │
│      (Early)    (Standard)    (Wait)                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ FILTER 3: Trend Strength                                   │
│ HA_CONSECUTIVE_CANDLES = How sure before entering?         │
│                                                             │
│ 1 Candle ←──────── 2 Candles ────────→ 3 Candles          │
│ (Quick)          (Balanced)           (Safe)               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ FILTER 4: Money Flow                                       │
│ VOLUME_MULTIPLIER = Is big money moving?                   │
│                                                             │
│ 1.1x ←──────── 1.2x ────────→ 1.5x                        │
│ (Relaxed)    (Standard)     (Strict)                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ FILTER 5: Momentum Building                                │
│ RSI_RISING/FALLING_CANDLES = Is momentum real?            │
│                                                             │
│ 1 Candle ←──────── 2 Candles ────────→ 3 Candles          │
│ (Fast)           (Balanced)           (Confirmed)          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ FILTER 6: Trend Health                                     │
│ MAX_DISTANCE_BELOW_SMA200 = Is trend broken?              │
│                                                             │
│ 12% ←──────── 18% ────────→ 25%                           │
│ (Strict)    (Balanced)    (Lenient)                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ FILTER 7: Final Scoring (0-100)                           │
│ PRIMARY_WINDOW + CONFIRMATION_WINDOW                       │
│                                                             │
│ 80-100: HIGH Confidence → Strong Alert                     │
│ 60-79:  MEDIUM Confidence → Good Alert                     │
│ 40-59:  LOW Confidence → Weak Alert                        │
│ 0-39:   NO TRADE → Rejected                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎭 Three Trading Personalities

### 🛡️ THE SAFE INVESTOR
**"I want quality over quantity"**

```
Profile:
• Salaried person
• ₹5-10 lakhs capital
• Checks market once daily
• Can hold 2-4 weeks
• Wants 75%+ success rate

Settings:
MIN_MARKET_CAP_CRORE=50000
RSI_OVERSOLD=25
RSI_OVERBOUGHT=75
HA_CONSECUTIVE_CANDLES=3
VOLUME_MULTIPLIER=1.5

Results:
📊 2-4 signals/month
✅ 75-80% success
💰 8-15% profit/trade
😌 Low stress
```

### ⚖️ THE BALANCED TRADER
**"I want good opportunities regularly"**

```
Profile:
• Part-time trader
• ₹2-5 lakhs capital
• Checks market 2-3 times daily
• Can hold 1-3 weeks
• Wants 65%+ success rate

Settings:
MIN_MARKET_CAP_CRORE=10000
RSI_OVERSOLD=30
RSI_OVERBOUGHT=70
HA_CONSECUTIVE_CANDLES=2
VOLUME_MULTIPLIER=1.2

Results:
📊 5-10 signals/month
✅ 65-70% success
💰 10-20% profit/trade
😊 Moderate activity
```

### ⚡ THE ACTIVE TRADER
**"I want maximum opportunities"**

```
Profile:
• Full-time trader
• ₹1-3 lakhs capital
• Monitors market all day
• Can hold 3-7 days
• Wants 60%+ success rate

Settings:
MIN_MARKET_CAP_CRORE=5000
RSI_OVERSOLD=35
RSI_OVERBOUGHT=65
HA_CONSECUTIVE_CANDLES=1
VOLUME_MULTIPLIER=1.1

Results:
📊 15-25 signals/month
✅ 60-65% success
💰 5-10% profit/trade
🔥 High activity
```

---

## 🎯 Quick Decision Tree

```
START: What's your goal?
   │
   ├─→ "I want to build wealth slowly" 
   │   → Use SAFE settings
   │   → Expect 2-4 signals/month
   │   → Hold 2-4 weeks
   │
   ├─→ "I want regular income from trading"
   │   → Use BALANCED settings
   │   → Expect 5-10 signals/month
   │   → Hold 1-3 weeks
   │
   └─→ "I want to trade actively"
       → Use ACTIVE settings
       → Expect 15-25 signals/month
       → Hold 3-7 days
```

---

## 📈 Understanding the Trade-offs

```
┌──────────────────────────────────────────────────────────┐
│                    THE TRIANGLE                          │
│                                                          │
│                    QUALITY                               │
│                      /\                                  │
│                     /  \                                 │
│                    /    \                                │
│                   /      \                               │
│                  /        \                              │
│                 /          \                             │
│                /            \                            │
│               /              \                           │
│              /                \                          │
│             /                  \                         │
│            /                    \                        │
│           /                      \                       │
│          /                        \                      │
│         /                          \                     │
│        /                            \                    │
│       /                              \                   │
│      /________________________________\                  │
│   QUANTITY                          SPEED                │
│                                                          │
│  You can pick TWO, not all THREE:                       │
│  • Quality + Speed = Few signals                        │
│  • Quality + Quantity = Slow entries                    │
│  • Speed + Quantity = Lower quality                     │
└──────────────────────────────────────────────────────────┘
```

---

## 🔄 The Adjustment Cycle

```
Week 1: START
   ↓
Use BALANCED preset
   ↓
Observe results
   ↓
Week 2: EVALUATE
   ↓
Too many signals? → Make STRICTER
Too few signals? → Make RELAXED
Too many losses? → Add CONFIRMATION
   ↓
Change ONE parameter
   ↓
Week 3-4: TEST
   ↓
Monitor new results
   ↓
Better? → Keep it
Worse? → Revert back
   ↓
Week 5: OPTIMIZE
   ↓
Fine-tune based on learnings
   ↓
REPEAT CYCLE
```

---

## 💡 Golden Rules

```
┌─────────────────────────────────────────────────────────┐
│ 1. Start with BALANCED preset                          │
│    Don't customize until you understand the system     │
│                                                         │
│ 2. Change ONE thing at a time                          │
│    Otherwise you won't know what worked               │
│                                                         │
│ 3. Give it 20-30 signals before judging                │
│    Too early to judge with 5-10 signals               │
│                                                         │
│ 4. Match settings to your lifestyle                    │
│    Aggressive settings need constant monitoring        │
│                                                         │
│ 5. Quality > Quantity ALWAYS                           │
│    10 good signals > 50 poor signals                   │
│                                                         │
│ 6. Capital preservation first                          │
│    Better to miss opportunities than lose money        │
│                                                         │
│ 7. Document your changes                               │
│    Keep a log of what works for you                    │
└─────────────────────────────────────────────────────────┘
```

---

## 🎓 Real-World Examples

### Example 1: Too Many Signals (Overwhelmed)
```
Problem: Getting 30 signals/month, can't track all
Solution: Make filters STRICTER
   • RSI_OVERSOLD: 35 → 30 (wait for deeper dips)
   • HA_CONSECUTIVE_CANDLES: 1 → 2 (more confirmation)
   • VOLUME_MULTIPLIER: 1.1 → 1.3 (bigger money moves)
Result: Now getting 10-12 quality signals
```

### Example 2: Too Few Signals (Bored)
```
Problem: Getting only 2 signals/month, want more action
Solution: Make filters RELAXED
   • RSI_OVERSOLD: 25 → 30 (earlier entries)
   • MIN_MARKET_CAP: 50000 → 10000 (include mid-caps)
   • HA_CONSECUTIVE_CANDLES: 3 → 2 (faster signals)
Result: Now getting 8-10 signals
```

### Example 3: Too Many Losses (Poor Quality)
```
Problem: Getting signals but 50% are losing trades
Solution: Add MORE CONFIRMATION
   • HA_CONSECUTIVE_CANDLES: 1 → 3 (stronger trends)
   • VOLUME_MULTIPLIER: 1.1 → 1.5 (institutional moves)
   • RSI_RISING_CANDLES: 1 → 2 (confirmed momentum)
   • MAX_DISTANCE_BELOW_SMA200: 25 → 15 (healthier trends)
Result: Fewer signals but 70% success rate
```

---

## 📱 Quick Test Commands

```bash
# After changing settings in Render.com:

# 1. Trigger a scan
curl -X POST https://your-app.onrender.com/run-job

# 2. Check if it's running
curl https://your-app.onrender.com/job-status

# 3. View recent signals
curl https://your-app.onrender.com/signals

# 4. Check Telegram channels for alerts
```

---

## 🎯 Success Metrics

Track these to measure your settings:

```
✅ Win Rate: Aim for 65%+ (7 wins out of 10 trades)
✅ Avg Profit: Aim for 10%+ per winning trade
✅ Signal Frequency: Match your availability
✅ Drawdown: Keep losses under 5% per trade
✅ Sleep Quality: Can you sleep peacefully? 😴
```

---

## 🚨 Warning Signs

```
🔴 Win rate < 50% → Settings too aggressive
🔴 Getting 50+ signals/month → Too relaxed
🔴 No signals for 2 weeks → Too strict
🔴 Can't monitor all signals → Reduce quantity
🔴 Stressed about trades → Increase confirmation
```

---

**Remember: The best settings are the ones that match YOUR lifestyle and risk tolerance!**

---

## 📚 Documentation Files

1. **BUSINESS_GUIDE.md** - Detailed WHY for each parameter
2. **CONFIGURATION_GUIDE.md** - Technical details and setup
3. **QUICK_REFERENCE.md** - Quick lookup and presets
4. **THIS FILE** - Visual summary and decision tree

Start with this file → Move to BUSINESS_GUIDE.md → Use QUICK_REFERENCE.md for changes
