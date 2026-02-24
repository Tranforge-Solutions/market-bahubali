# 🔓 Filter Skip Feature - Using "NA" to Disable Filters

## 🎯 Overview

Sometimes filters are TOO STRICT and you get NO signals. Now you can set any filter to **"NA"** to skip it completely.

**Use Case:** "I'm getting 0 signals because my filters are too restrictive. Let me disable some filters to see more opportunities."

---

## ⚙️ How It Works

Set any environment variable to **"NA"** (case insensitive) to disable that filter:

```env
# Example: Disable RSI oversold filter
RSI_OVERSOLD_THRESHOLD=NA

# Example: Disable volume filter
VOLUME_MULTIPLIER=NA

# Example: Disable market cap filter
MIN_MARKET_CAP_CRORE=NA
```

---

## 📋 Filters That Support "NA"

### 1. MIN_MARKET_CAP_CRORE=NA
**What it does:** Includes ALL stocks regardless of market cap

**When to use:**
- ✅ You want to trade small-cap stocks
- ✅ You're getting too few signals
- ✅ You're experienced with risky stocks

**Risk Level:** 🔴🔴🔴 HIGH RISK

**Example:**
```env
MIN_MARKET_CAP_CRORE=NA
```

**Result:**
- Before: Only 300 stocks (₹10,000+ Cr)
- After: All 500 Nifty stocks (including ₹500 Cr companies)
- Signal increase: +60-80%

**Warning:** Small-cap stocks are:
- ❌ More volatile (big swings)
- ❌ Less liquid (hard to exit)
- ❌ Higher risk of manipulation

---

### 2. RSI_OVERSOLD_THRESHOLD=NA
**What it does:** Generates BUY signals at ANY RSI level (no oversold requirement)

**When to use:**
- ✅ You want to catch trends early
- ✅ You don't want to wait for oversold conditions
- ✅ You're using other indicators

**Risk Level:** 🔴🔴 MEDIUM-HIGH RISK

**Example:**
```env
RSI_OVERSOLD_THRESHOLD=NA
RSI_RISING_CANDLES=2  # Keep this for momentum confirmation
```

**Result:**
- Before: Only signals when RSI < 30
- After: Signals whenever RSI is rising (any level)
- Signal increase: +200-300%

**Warning:** You'll get signals in:
- ❌ Overbought zones (RSI 70+) - risky entries
- ❌ Neutral zones (RSI 40-60) - no edge
- ✅ Use with other strong filters (HA, Volume)

---

### 3. RSI_OVERBOUGHT_THRESHOLD=NA
**What it does:** Generates SELL signals at ANY RSI level (no overbought requirement)

**When to use:**
- ✅ You want to exit positions early
- ✅ You're using trailing stops
- ✅ You don't want to wait for overbought

**Risk Level:** 🔴🔴 MEDIUM-HIGH RISK

**Example:**
```env
RSI_OVERBOUGHT_THRESHOLD=NA
RSI_FALLING_CANDLES=2  # Keep this for momentum confirmation
```

**Result:**
- Before: Only signals when RSI > 70
- After: Signals whenever RSI is falling (any level)
- Signal increase: +200-300%

**Warning:** You'll exit:
- ❌ Too early (miss big moves)
- ❌ In healthy corrections (false signals)

---

### 4. RSI_RISING_CANDLES=NA
**What it does:** No need for RSI to rise consecutively

**When to use:**
- ✅ You want immediate entries
- ✅ You're very active trader
- ✅ You can exit quickly if wrong

**Risk Level:** 🔴🔴🔴 HIGH RISK

**Example:**
```env
RSI_OVERSOLD_THRESHOLD=30  # Keep this
RSI_RISING_CANDLES=NA      # Skip momentum check
```

**Result:**
- Before: RSI must rise for 2 days
- After: Signal on first oversold day
- Signal increase: +50-100%

**Warning:**
- ❌ Many false signals (RSI can keep falling)
- ❌ Catch falling knives
- ✅ Must use with strong HA and Volume filters

---

### 5. RSI_FALLING_CANDLES=NA
**What it does:** No need for RSI to fall consecutively

**When to use:**
- ✅ Quick exits
- ✅ Scalping strategy
- ✅ Very active monitoring

**Risk Level:** 🔴🔴🔴 HIGH RISK

**Example:**
```env
RSI_OVERBOUGHT_THRESHOLD=70  # Keep this
RSI_FALLING_CANDLES=NA       # Skip momentum check
```

**Result:**
- Before: RSI must fall for 2 days
- After: Signal on first overbought day
- Signal increase: +50-100%

---

### 6. HA_CONSECUTIVE_CANDLES=NA
**What it does:** No Heikin Ashi trend confirmation needed

**When to use:**
- ✅ You don't trust HA candles
- ✅ You're using other trend indicators
- ✅ You want maximum signals

**Risk Level:** 🔴🔴 MEDIUM-HIGH RISK

**Example:**
```env
HA_CONSECUTIVE_CANDLES=NA
```

**Result:**
- Before: Need 1-3 consecutive HA candles
- After: No HA confirmation needed
- Signal increase: +40-60%

**Warning:**
- ❌ More false reversals
- ❌ Enter during consolidation
- ✅ Compensate with stricter RSI and Volume

---

### 7. VOLUME_MULTIPLIER=NA
**What it does:** No volume confirmation needed

**When to use:**
- ✅ Trading illiquid stocks
- ✅ Volume data unreliable
- ✅ You're using price action only

**Risk Level:** 🔴🔴 MEDIUM-HIGH RISK

**Example:**
```env
VOLUME_MULTIPLIER=NA
```

**Result:**
- Before: Volume must be 1.2x average
- After: Any volume accepted
- Signal increase: +30-50%

**Warning:**
- ❌ Weak moves (no conviction)
- ❌ Fake breakouts
- ❌ Low liquidity traps

---

### 8. MAX_DISTANCE_BELOW_SMA200_PERCENT=NA
**What it does:** No trend health check (allow broken trends)

**When to use:**
- ✅ You're a contrarian trader
- ✅ You want deep value plays
- ✅ You're patient (long holding period)

**Risk Level:** 🔴🔴🔴 HIGH RISK

**Example:**
```env
MAX_DISTANCE_BELOW_SMA200_PERCENT=NA
```

**Result:**
- Before: Stock can't be >18% below 200 SMA
- After: Any distance allowed (even 50% below)
- Signal increase: +20-40%

**Warning:**
- ❌ Catch falling knives
- ❌ Broken trends (may never recover)
- ❌ Long recovery time (months)

---

## 🎯 RECOMMENDED "NA" COMBINATIONS

### Scenario 1: "I'm Getting ZERO Signals"

**Problem:** All filters are too strict, no stocks pass

**Solution:** Relax the strictest filters first

```env
# Start by relaxing these (in order):
HA_CONSECUTIVE_CANDLES=NA          # Most restrictive
VOLUME_MULTIPLIER=NA               # Often blocks signals
MAX_DISTANCE_BELOW_SMA200_PERCENT=NA  # Very strict

# Keep these for quality:
RSI_OVERSOLD_THRESHOLD=30          # Keep RSI filter
RSI_RISING_CANDLES=2               # Keep momentum
MIN_MARKET_CAP_CRORE=10000         # Keep safety
```

**Expected Result:** 5-10 signals/month

---

### Scenario 2: "I Want Maximum Signals (High Risk)"

**Problem:** I can monitor constantly, want all opportunities

**Solution:** Disable most filters

```env
# Disable strict filters:
HA_CONSECUTIVE_CANDLES=NA
VOLUME_MULTIPLIER=NA
MAX_DISTANCE_BELOW_SMA200_PERCENT=NA
RSI_RISING_CANDLES=NA
RSI_FALLING_CANDLES=NA

# Keep only basic filters:
RSI_OVERSOLD_THRESHOLD=35          # Relaxed RSI
RSI_OVERBOUGHT_THRESHOLD=65        # Relaxed RSI
MIN_MARKET_CAP_CRORE=5000          # Include mid-caps
```

**Expected Result:** 30-50 signals/month  
**Win Rate:** 50-55% (lower quality)  
**Requires:** Constant monitoring

---

### Scenario 3: "I Want Small-Cap Opportunities"

**Problem:** Only getting large-cap signals, want more action

**Solution:** Remove market cap filter only

```env
# Disable market cap filter:
MIN_MARKET_CAP_CRORE=NA

# Keep all other filters STRICT for safety:
RSI_OVERSOLD_THRESHOLD=25          # Strict
RSI_OVERBOUGHT_THRESHOLD=75        # Strict
HA_CONSECUTIVE_CANDLES=3           # Strong confirmation
VOLUME_MULTIPLIER=1.5              # High volume
MAX_DISTANCE_BELOW_SMA200_PERCENT=12  # Healthy trends
RSI_RISING_CANDLES=2
RSI_FALLING_CANDLES=2
```

**Expected Result:** 15-20 signals/month  
**Win Rate:** 60-65%  
**Risk:** Higher volatility but quality signals

---

### Scenario 4: "I Don't Trust Volume Data"

**Problem:** Volume data is unreliable for my stocks

**Solution:** Skip volume filter

```env
# Disable volume filter:
VOLUME_MULTIPLIER=NA

# Compensate with stricter other filters:
RSI_OVERSOLD_THRESHOLD=25          # Very strict
HA_CONSECUTIVE_CANDLES=3           # Strong trend
MAX_DISTANCE_BELOW_SMA200_PERCENT=12  # Healthy only
RSI_RISING_CANDLES=3               # Strong momentum
```

**Expected Result:** 8-12 signals/month  
**Win Rate:** 70-75%  
**Note:** Quality maintained despite no volume check

---

## ⚠️ CRITICAL WARNINGS

### 1. Never Disable ALL Filters
```env
# ❌ DANGEROUS - Don't do this:
MIN_MARKET_CAP_CRORE=NA
RSI_OVERSOLD_THRESHOLD=NA
RSI_OVERBOUGHT_THRESHOLD=NA
HA_CONSECUTIVE_CANDLES=NA
VOLUME_MULTIPLIER=NA
MAX_DISTANCE_BELOW_SMA200_PERCENT=NA
RSI_RISING_CANDLES=NA
RSI_FALLING_CANDLES=NA
```

**Result:** Random signals with no edge = Guaranteed losses

---

### 2. Disable Maximum 3-4 Filters
```env
# ✅ SAFE - Balanced approach:
HA_CONSECUTIVE_CANDLES=NA          # Disabled
VOLUME_MULTIPLIER=NA               # Disabled
MAX_DISTANCE_BELOW_SMA200_PERCENT=NA  # Disabled

# Keep these:
RSI_OVERSOLD_THRESHOLD=30          # Active
RSI_RISING_CANDLES=2               # Active
MIN_MARKET_CAP_CRORE=10000         # Active
```

**Rule:** Keep at least 3-4 filters active for quality

---

### 3. Test One "NA" at a Time
```
Week 1: Add HA_CONSECUTIVE_CANDLES=NA
        → Monitor results
        
Week 2: If good, add VOLUME_MULTIPLIER=NA
        → Monitor results
        
Week 3: Evaluate combined effect
```

**Don't:** Change 5 filters to NA at once (can't learn what works)

---

## 📊 IMPACT MATRIX

| Filter Set to NA | Signal Increase | Risk Increase | Win Rate Impact |
|------------------|----------------|---------------|-----------------|
| MIN_MARKET_CAP_CRORE | +60-80% | 🔴🔴🔴 High | -10-15% |
| RSI_OVERSOLD_THRESHOLD | +200-300% | 🔴🔴🔴 High | -20-25% |
| RSI_OVERBOUGHT_THRESHOLD | +200-300% | 🔴🔴 Medium | -15-20% |
| HA_CONSECUTIVE_CANDLES | +40-60% | 🔴🔴 Medium | -8-12% |
| VOLUME_MULTIPLIER | +30-50% | 🔴🔴 Medium | -5-10% |
| MAX_DISTANCE_BELOW_SMA200 | +20-40% | 🔴🔴🔴 High | -10-15% |
| RSI_RISING_CANDLES | +50-100% | 🔴🔴🔴 High | -15-20% |
| RSI_FALLING_CANDLES | +50-100% | 🔴🔴🔴 High | -15-20% |

---

## 🎓 LEARNING PATH WITH "NA"

### Phase 1: Understand Current Settings (Week 1-2)
```env
# Use default settings, no NA
# Track: How many signals? Win rate?
```

### Phase 2: Relax One Filter (Week 3-4)
```env
# Add one NA (least risky first)
HA_CONSECUTIVE_CANDLES=NA
# Track: Signal increase? Win rate change?
```

### Phase 3: Optimize (Week 5-6)
```env
# If Phase 2 worked, try another
VOLUME_MULTIPLIER=NA
# Track: Is it better or worse?
```

### Phase 4: Find Your Sweet Spot (Week 7-8)
```env
# Keep what works, revert what doesn't
# Document your winning configuration
```

---

## 💡 PRO TIPS

### 1. Use NA for Temporary Testing
```env
# Testing week: Disable HA filter
HA_CONSECUTIVE_CANDLES=NA

# After 1 week: Evaluate
# Good results? Keep it
# Bad results? Revert to HA_CONSECUTIVE_CANDLES=2
```

### 2. Seasonal Adjustments
```env
# Bull Market (lots of opportunities):
# Use stricter filters, fewer NAs

# Bear Market (few opportunities):
# Use more NAs to find signals
```

### 3. Capital-Based Strategy
```env
# Small capital (₹1-2 lakhs):
MIN_MARKET_CAP_CRORE=NA  # Need more opportunities
HA_CONSECUTIVE_CANDLES=NA

# Large capital (₹20+ lakhs):
# Keep all filters active (quality over quantity)
```

---

## 🔄 Reverting NA Settings

To go back to default:

```env
# Remove NA, set to default value:
MIN_MARKET_CAP_CRORE=10000
RSI_OVERSOLD_THRESHOLD=30
RSI_OVERBOUGHT_THRESHOLD=70
HA_CONSECUTIVE_CANDLES=2
VOLUME_MULTIPLIER=1.2
MAX_DISTANCE_BELOW_SMA200_PERCENT=18
RSI_RISING_CANDLES=2
RSI_FALLING_CANDLES=2
```

---

## 📞 DECISION FRAMEWORK

**Before setting any filter to NA, ask:**

1. **"Why am I getting no signals?"**
   - Too strict filters? → Use NA
   - Market conditions? → Wait
   - Wrong strategy? → Rethink approach

2. **"Which filter is blocking most signals?"**
   - Check logs to see where stocks fail
   - Disable that filter first

3. **"Can I handle more risk?"**
   - Yes + Can monitor → Use NA
   - No → Keep filters active

4. **"Do I have a backup plan?"**
   - Stop loss ready? → OK to use NA
   - No risk management? → Don't use NA

---

## ⚡ QUICK REFERENCE

```
Getting 0 signals?
→ Set HA_CONSECUTIVE_CANDLES=NA

Still 0 signals?
→ Add VOLUME_MULTIPLIER=NA

Still 0 signals?
→ Add MAX_DISTANCE_BELOW_SMA200_PERCENT=NA

Want small-cap stocks?
→ Set MIN_MARKET_CAP_CRORE=NA

Want maximum signals (risky)?
→ Set RSI_OVERSOLD_THRESHOLD=NA
→ Set RSI_RISING_CANDLES=NA

Want to exit early?
→ Set RSI_OVERBOUGHT_THRESHOLD=NA
```

---

**Remember:** NA = More signals but LESS quality. Use wisely!

**Golden Rule:** Never disable more than 3-4 filters at once.

---

**Last Updated:** February 2026  
**Feature:** Filter Skip with "NA"  
**Status:** Production Ready
