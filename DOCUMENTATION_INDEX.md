# 📚 Documentation Index - Market Monitoring System

## 🎯 Start Here

Welcome! This system automatically scans 500+ stocks and alerts you when perfect buy/sell opportunities appear.

---

## 📖 Documentation Files (Read in Order)

### 1. **VISUAL_SUMMARY.md** ⭐ START HERE
**Read this first!** One-page visual guide with:
- What the system does
- The 7 filters explained visually
- 3 trading personality presets
- Quick decision tree
- Real-world examples

**Time:** 10 minutes  
**For:** Everyone (beginners to experts)

---

### 2. **BUSINESS_GUIDE.md** ⭐ MUST READ
**Deep dive into WHY each parameter exists**
- Business perspective for each filter
- Real-world trading scenarios
- Risk vs reward explanations
- 3 detailed user profiles with settings
- Decision framework

**Time:** 30 minutes  
**For:** Anyone configuring the system

---

### 3. **PRODUCTION_SETTINGS_EXPLAINED.md**
**Understanding current production settings**
- Exact settings currently running
- Why each value was chosen
- Complete filtering example (ICICI Bank walkthrough)
- Expected monthly performance
- When to adjust settings

**Time:** 20 minutes  
**For:** Understanding what's deployed now

---

### 4. **FILTER_SKIP_NA_GUIDE.md** ⭐ IMPORTANT
**How to disable filters when too strict**
- Use "NA" to skip any filter
- When you're getting ZERO signals
- Risk levels for each NA option
- Recommended NA combinations
- Impact matrix

**Time:** 15 minutes  
**For:** When filters are too restrictive

---

### 5. **CONFIGURATION_GUIDE.md**
**Technical configuration details**
- All environment variables explained
- How to set up Telegram
- Database configuration
- Preset configurations
- Troubleshooting guide

**Time:** 25 minutes  
**For:** Initial setup and technical details

---

### 6. **QUICK_REFERENCE.md**
**Quick lookup card**
- Copy-paste configurations
- Parameter cheat sheet
- Common adjustments
- Emergency reset values
- Testing commands

**Time:** 5 minutes  
**For:** Quick reference during changes

---

## 🚀 Quick Start Guide

### For Complete Beginners:

```
Step 1: Read VISUAL_SUMMARY.md (10 min)
        ↓
Step 2: Read BUSINESS_GUIDE.md (30 min)
        ↓
Step 3: Choose a preset from VISUAL_SUMMARY.md
        ↓
Step 4: Set up environment variables (CONFIGURATION_GUIDE.md)
        ↓
Step 5: Run for 1 week, monitor results
        ↓
Step 6: Adjust using QUICK_REFERENCE.md
```

### For Experienced Traders:

```
Step 1: Read VISUAL_SUMMARY.md (10 min)
        ↓
Step 2: Read PRODUCTION_SETTINGS_EXPLAINED.md (20 min)
        ↓
Step 3: Customize based on your style
        ↓
Step 4: Use FILTER_SKIP_NA_GUIDE.md if needed
```

---

## 🎯 Common Scenarios

### "I'm getting ZERO signals"
→ Read: **FILTER_SKIP_NA_GUIDE.md**  
→ Solution: Set some filters to "NA"

### "I don't understand why we need these filters"
→ Read: **BUSINESS_GUIDE.md**  
→ Explains the business logic behind each filter

### "What settings are currently running?"
→ Read: **PRODUCTION_SETTINGS_EXPLAINED.md**  
→ Shows exact production configuration

### "I want to change settings quickly"
→ Read: **QUICK_REFERENCE.md**  
→ Copy-paste ready configurations

### "I'm setting this up for the first time"
→ Read: **CONFIGURATION_GUIDE.md**  
→ Complete setup instructions

---

## 📊 Documentation Summary

| Document | Purpose | Time | Audience |
|----------|---------|------|----------|
| VISUAL_SUMMARY.md | Quick overview | 10 min | Everyone |
| BUSINESS_GUIDE.md | WHY each filter exists | 30 min | Decision makers |
| PRODUCTION_SETTINGS_EXPLAINED.md | Current settings | 20 min | Operators |
| FILTER_SKIP_NA_GUIDE.md | Disable strict filters | 15 min | Advanced users |
| CONFIGURATION_GUIDE.md | Technical setup | 25 min | Admins |
| QUICK_REFERENCE.md | Quick lookup | 5 min | Everyone |

---

## 🎓 Learning Path

### Week 1: Understanding
- Read VISUAL_SUMMARY.md
- Read BUSINESS_GUIDE.md
- Choose a preset (Safe/Balanced/Aggressive)
- Deploy with chosen preset

### Week 2: Monitoring
- Track signals received
- Track win rate
- Note any issues (too many/few signals)

### Week 3: First Adjustment
- Read QUICK_REFERENCE.md
- Make ONE change based on Week 2 results
- Document the change

### Week 4: Evaluation
- Compare Week 3 vs Week 2
- Better? Keep the change
- Worse? Revert back

### Month 2: Optimization
- Fine-tune based on learnings
- Use FILTER_SKIP_NA_GUIDE.md if needed
- Document your winning configuration

---

## 💡 Key Concepts

### The 7 Filters (In Order):
1. **Market Cap** - Company size filter
2. **RSI Level** - Price oversold/overbought
3. **RSI Momentum** - Rising/falling confirmation
4. **Heikin Ashi** - Trend direction
5. **Volume** - Money flow confirmation
6. **Trend Health** - Not too far from 200 SMA
7. **Scoring** - Final 0-100 score

### The Trade-off Triangle:
```
You can pick TWO, not all THREE:
- Quality (high win rate)
- Quantity (many signals)
- Speed (early entries)
```

### The NA Feature:
```
Set any filter to "NA" to skip it
Example: HA_CONSECUTIVE_CANDLES=NA
Result: More signals, less quality
```

---

## 🎯 Three Trading Profiles

### 🛡️ Safe Investor
- **Signals:** 2-4/month
- **Win Rate:** 75-80%
- **Monitoring:** Once daily
- **Capital:** ₹5-10 lakhs
- **Read:** BUSINESS_GUIDE.md → Scenario 1

### ⚖️ Balanced Trader
- **Signals:** 5-10/month
- **Win Rate:** 65-70%
- **Monitoring:** 2-3 times daily
- **Capital:** ₹2-5 lakhs
- **Read:** PRODUCTION_SETTINGS_EXPLAINED.md

### ⚡ Active Trader
- **Signals:** 15-25/month
- **Win Rate:** 60-65%
- **Monitoring:** All day
- **Capital:** ₹1-3 lakhs
- **Read:** FILTER_SKIP_NA_GUIDE.md

---

## 🔧 Environment Variables Quick Reference

### Must Configure:
```env
TELEGRAM_BOT_TOKEN=<from @BotFather>
TELEGRAM_CHAT_ID=<from @userinfobot>
TELEGRAM_BUY_CHANNEL_ID=<your channel with - sign>
TELEGRAM_SELL_CHANNEL_ID=<your channel with - sign>
DATABASE_URL=<from Render.com>
```

### Can Customize:
```env
MIN_MARKET_CAP_CRORE=10000 (or NA)
RSI_OVERSOLD_THRESHOLD=30 (or NA)
RSI_OVERBOUGHT_THRESHOLD=70 (or NA)
HA_CONSECUTIVE_CANDLES=2 (or NA)
VOLUME_MULTIPLIER=1.2 (or NA)
MAX_DISTANCE_BELOW_SMA200_PERCENT=18 (or NA)
RSI_RISING_CANDLES=2 (or NA)
RSI_FALLING_CANDLES=2 (or NA)
```

---

## ⚠️ Important Rules

1. **Start with a preset** - Don't customize immediately
2. **Change ONE thing at a time** - Can't learn otherwise
3. **Give it 20-30 signals** - Too early to judge with 5-10
4. **Never disable ALL filters** - Need at least 3-4 active
5. **Document your changes** - Keep a log
6. **Match settings to lifestyle** - Aggressive needs monitoring

---

## 📞 Support & Troubleshooting

### No signals?
1. Check FILTER_SKIP_NA_GUIDE.md
2. Set HA_CONSECUTIVE_CANDLES=NA
3. Set VOLUME_MULTIPLIER=NA

### Too many signals?
1. Check QUICK_REFERENCE.md
2. Make filters stricter
3. Increase HA_CONSECUTIVE_CANDLES

### Poor win rate?
1. Check BUSINESS_GUIDE.md
2. Add more confirmation
3. Increase VOLUME_MULTIPLIER

### Don't understand a parameter?
1. Check BUSINESS_GUIDE.md
2. See real-world examples
3. Understand the WHY

---

## 🎯 Success Metrics

Track these to measure your settings:

```
✅ Win Rate: Aim for 65%+ (7 wins out of 10)
✅ Avg Profit: Aim for 10%+ per trade
✅ Signal Frequency: Match your availability
✅ Drawdown: Keep losses under 5% per trade
✅ Sleep Quality: Can you sleep peacefully? 😴
```

---

## 📱 API Endpoints

```bash
# Trigger manual scan
curl -X POST https://your-app.onrender.com/run-job

# Check job status
curl https://your-app.onrender.com/job-status

# View recent signals
curl https://your-app.onrender.com/signals

# Check health
curl https://your-app.onrender.com/health
```

---

## 🎓 Recommended Reading Order

### First Time Setup:
1. VISUAL_SUMMARY.md (understand the system)
2. CONFIGURATION_GUIDE.md (set it up)
3. BUSINESS_GUIDE.md (understand the logic)

### Daily Operations:
1. QUICK_REFERENCE.md (quick changes)
2. PRODUCTION_SETTINGS_EXPLAINED.md (current state)

### Troubleshooting:
1. FILTER_SKIP_NA_GUIDE.md (too few signals)
2. BUSINESS_GUIDE.md (understand impact)
3. QUICK_REFERENCE.md (make changes)

---

## 💡 Pro Tips

1. **Bookmark QUICK_REFERENCE.md** - You'll use it most
2. **Print VISUAL_SUMMARY.md** - Keep it handy
3. **Re-read BUSINESS_GUIDE.md** - Deeper understanding each time
4. **Use FILTER_SKIP_NA_GUIDE.md** - When stuck with no signals
5. **Check PRODUCTION_SETTINGS_EXPLAINED.md** - Before major changes

---

## 🚨 Emergency Contacts

### System not working?
1. Check `/job-status` endpoint
2. Check Render.com logs
3. Verify environment variables

### Getting errors?
1. Check DATABASE_URL is correct
2. Check TELEGRAM_BOT_TOKEN is valid
3. Check channel IDs have negative sign

### Need to reset?
1. Go to QUICK_REFERENCE.md
2. Use "Emergency Reset" section
3. Copy default values

---

## 📚 Additional Resources

- **GitHub Repository:** [Link to repo]
- **Render.com Dashboard:** [Your deployment]
- **Telegram Bot:** @Market_bahubali_bot
- **Support:** [Your contact]

---

## 🎯 Final Checklist

Before going live:

- [ ] Read VISUAL_SUMMARY.md
- [ ] Read BUSINESS_GUIDE.md
- [ ] Chose a preset (Safe/Balanced/Aggressive)
- [ ] Set up Telegram bot and channels
- [ ] Configured environment variables
- [ ] Tested with `/run-job`
- [ ] Verified signals in Telegram
- [ ] Documented your configuration
- [ ] Set up monitoring routine
- [ ] Prepared to track results

---

**Remember:** The best settings are the ones that let you sleep peacefully at night!

**Start with:** VISUAL_SUMMARY.md → BUSINESS_GUIDE.md → Choose preset → Monitor → Optimize

---

**Last Updated:** February 2026  
**Version:** 2.0 (with NA filter skip feature)  
**Status:** Production Ready
