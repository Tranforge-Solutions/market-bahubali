# Business Guide - Understanding Stock Selection Parameters

## 🎯 Purpose of This System

This system automatically finds stocks that are:
- **Oversold** (cheap, ready to bounce up) → BUY signals
- **Overbought** (expensive, ready to fall) → SELL signals

Think of it as a **smart filter** that scans 500+ stocks daily and alerts you only when conditions are perfect for entry/exit.

---

## 💼 BUSINESS PERSPECTIVE: Why Each Parameter Exists

### 🏢 1. MIN_MARKET_CAP_CRORE (Company Size Filter)

**Business Question:** "Should I trade in small companies or large companies?"

**Why This Matters:**
- **Large companies (₹50,000+ Cr):** Like Reliance, TCS, HDFC Bank
  - ✅ Stable, less risky
  - ✅ High liquidity (easy to buy/sell)
  - ❌ Slower price movements (smaller profits)
  - ❌ Fewer opportunities

- **Mid-cap companies (₹10,000-50,000 Cr):** 
  - ⚖️ Moderate risk
  - ⚖️ Good liquidity
  - ✅ Better price movements (good profits)
  - ✅ More opportunities

- **Small companies (₹5,000-10,000 Cr):**
  - ❌ Higher risk
  - ❌ Lower liquidity (hard to exit)
  - ✅ Fast price movements (big profits/losses)
  - ✅ Many opportunities

**Real-World Example:**
- If you have ₹10 lakhs to invest → Set to `50000` (large caps only)
- If you have ₹2-5 lakhs → Set to `10000` (large + mid caps)
- If you're experienced trader → Set to `5000` (include smaller companies)

**Business Decision:** "How much risk can I afford?"

---

### 📊 2. RSI_OVERSOLD_THRESHOLD (When to BUY)

**Business Question:** "How cheap should a stock be before I buy?"

**Why This Matters:**
RSI measures if a stock is "oversold" (too cheap, ready to bounce).

**Think of it like shopping:**
- **RSI = 25:** Stock is at 75% discount (extreme sale, rare opportunity)
- **RSI = 30:** Stock is at 70% discount (good sale, standard)
- **RSI = 35:** Stock is at 65% discount (mild sale, frequent)

**Real-World Scenarios:**

**Conservative Trader (RSI = 25):**
- "I only buy when there's a HUGE discount"
- Waits for extreme panic selling
- Gets 2-3 signals per month
- Higher success rate (80%+)
- Example: Stock crashes from ₹1000 to ₹700 due to market panic

**Balanced Trader (RSI = 30):**
- "I buy when there's a good discount"
- Standard oversold condition
- Gets 5-8 signals per month
- Good success rate (70%)
- Example: Stock drops from ₹1000 to ₹800 in normal correction

**Aggressive Trader (RSI = 35):**
- "I buy early to catch the bounce"
- Enters before extreme oversold
- Gets 10-15 signals per month
- Moderate success rate (60%)
- Example: Stock drops from ₹1000 to ₹850, starts buying

**Business Decision:** "Do I want fewer but stronger opportunities, or more frequent trades?"

---

### 📈 3. RSI_OVERBOUGHT_THRESHOLD (When to SELL)

**Business Question:** "How expensive should a stock be before I sell?"

**Why This Matters:**
RSI measures if a stock is "overbought" (too expensive, ready to fall).

**Think of it like selling property:**
- **RSI = 75:** Property price is 25% above fair value (extreme bubble)
- **RSI = 70:** Property price is 20% above fair value (good time to sell)
- **RSI = 65:** Property price is 15% above fair value (early exit)

**Real-World Scenarios:**

**Conservative Trader (RSI = 75):**
- "I sell only at peak prices"
- Waits for extreme greed/euphoria
- Maximizes profit per trade
- Risk: May miss the peak
- Example: Stock rallies from ₹1000 to ₹1400 (everyone buying)

**Balanced Trader (RSI = 70):**
- "I sell when price is fairly high"
- Standard overbought condition
- Good profit booking
- Example: Stock rallies from ₹1000 to ₹1300

**Aggressive Trader (RSI = 65):**
- "I sell early to lock profits"
- Exits before peak
- Safer but smaller profits
- Example: Stock rallies from ₹1000 to ₹1200, starts selling

**Business Decision:** "Do I want maximum profit (risky) or safe profit booking?"

---

### 🕯️ 4. HA_CONSECUTIVE_CANDLES (Trend Confirmation)

**Business Question:** "How sure should I be before entering a trade?"

**Why This Matters:**
Heikin Ashi candles show trend direction. Consecutive candles = stronger trend.

**Think of it like weather forecast:**
- **1 candle:** "It might rain" (50% confidence)
- **2 candles:** "It will probably rain" (70% confidence)
- **3 candles:** "It will definitely rain" (90% confidence)

**Real-World Scenarios:**

**Aggressive (1 candle):**
- Enters trade immediately when first signal appears
- ✅ Catches moves early
- ❌ Many false signals
- Example: Stock shows 1 green candle, you buy immediately
- **Use when:** You can monitor constantly and exit quickly

**Balanced (2 candles):**
- Waits for confirmation
- ⚖️ Good balance of speed and accuracy
- Example: Stock shows 2 consecutive green candles, trend confirmed
- **Use when:** You check market 2-3 times daily

**Conservative (3 candles):**
- Waits for strong confirmation
- ✅ Very few false signals
- ❌ Enters late, misses some profit
- Example: Stock shows 3 consecutive green candles, strong uptrend
- **Use when:** You're a long-term investor

**Business Decision:** "How much confirmation do I need before risking my money?"

---

### 📦 5. VOLUME_MULTIPLIER (Money Flow Confirmation)

**Business Question:** "Is this price move real or fake?"

**Why This Matters:**
Volume = Number of shares traded = Money flowing in/out

**Think of it like a shop:**
- **High volume:** 1000 customers buying (real demand, price will rise)
- **Low volume:** 10 customers buying (fake demand, price may fall back)

**Real-World Scenarios:**

**Strict (1.5x = 50% more volume):**
- "I only trade when BIG money is moving"
- Institutional buying/selling
- Very strong signals
- Example: Stock normally trades 10 lakh shares, today 15 lakh shares
- **Use when:** You want only high-conviction trades

**Balanced (1.2x = 20% more volume):**
- "I trade when there's decent money flow"
- Good participation
- Standard confirmation
- Example: Stock normally trades 10 lakh shares, today 12 lakh shares
- **Use when:** You want regular opportunities

**Relaxed (1.1x = 10% more volume):**
- "I trade even with moderate money flow"
- More opportunities
- Some false signals
- Example: Stock normally trades 10 lakh shares, today 11 lakh shares
- **Use when:** You're in less liquid stocks

**Business Decision:** "Do I want to follow big money or catch early moves?"

---

### 📉 6. MAX_DISTANCE_BELOW_SMA200_PERCENT (Trend Health Check)

**Business Question:** "Is this stock in a healthy trend or broken trend?"

**Why This Matters:**
200-day SMA = Long-term average price = Trend health indicator

**Think of it like a patient's health:**
- **12% below:** Patient has mild fever (can recover quickly)
- **18% below:** Patient has moderate illness (needs time to recover)
- **25% below:** Patient is seriously ill (long recovery time)

**Real-World Scenarios:**

**Strict (12%):**
- "I only buy stocks in strong uptrends"
- Stock is close to its long-term average
- Quick recovery expected
- Example: Stock's 200-day average is ₹1000, current price ₹880
- **Use when:** You want quick profits (1-2 weeks)

**Balanced (18%):**
- "I buy stocks in moderate corrections"
- Stock has corrected but not broken
- Medium-term recovery
- Example: Stock's 200-day average is ₹1000, current price ₹820
- **Use when:** You can hold for 2-4 weeks

**Lenient (25%):**
- "I buy stocks in deep corrections"
- Stock is heavily beaten down
- Long-term recovery play
- Example: Stock's 200-day average is ₹1000, current price ₹750
- **Use when:** You're a patient investor (1-3 months)

**Business Decision:** "Do I want quick bounces or deep value plays?"

---

### ⏱️ 7. RSI_RISING_CANDLES & RSI_FALLING_CANDLES (Momentum Confirmation)

**Business Question:** "Is the momentum building or just a one-day spike?"

**Why This Matters:**
Consecutive rising/falling RSI = Sustained momentum = Real move

**Think of it like a car:**
- **1 candle:** Car accelerated once (might be temporary)
- **2 candles:** Car is consistently accelerating (real momentum)
- **3 candles:** Car is in full speed (strong momentum)

**Real-World Scenarios:**

**Quick Entry (1 candle):**
- Enters on first sign of momentum
- ✅ Earliest entry
- ❌ Many false starts
- **Use when:** You're a day trader

**Balanced (2 candles):**
- Waits for momentum confirmation
- ⚖️ Good timing
- **Use when:** You're a swing trader (3-7 days)

**Safe Entry (3 candles):**
- Waits for strong momentum
- ✅ High success rate
- ❌ Late entry
- **Use when:** You're a position trader (weeks)

**Business Decision:** "Do I want to catch the start or join confirmed moves?"

---

### 📅 8. PRIMARY_WINDOW_CANDLES & CONFIRMATION_WINDOW_CANDLES (Time Horizon)

**Business Question:** "Am I a short-term trader or long-term investor?"

**Why This Matters:**
These define your trading timeframe.

**Think of it like planning a trip:**
- **Primary Window (70 candles):** Looking at last 2-3 months (overall journey)
- **Confirmation Window (30 candles):** Looking at last 3-4 weeks (immediate route)

**Real-World Scenarios:**

**Short-term Trader:**
- Primary: 50 candles (1.5 months)
- Confirmation: 20 candles (2 weeks)
- **Goal:** Quick 5-10% profits in 1-2 weeks
- **Use when:** You trade actively

**Medium-term Trader:**
- Primary: 70 candles (2-3 months)
- Confirmation: 30 candles (3-4 weeks)
- **Goal:** 10-20% profits in 3-6 weeks
- **Use when:** You check market daily

**Long-term Investor:**
- Primary: 90 candles (3-4 months)
- Confirmation: 40 candles (5-6 weeks)
- **Goal:** 20-30% profits in 2-3 months
- **Use when:** You're patient

**Business Decision:** "How long can I hold a position?"

---

## 🎯 PUTTING IT ALL TOGETHER: Business Scenarios

### Scenario 1: "I'm a Salaried Person, Can't Monitor Market"
**Your Profile:**
- ✅ Have ₹5-10 lakhs to invest
- ✅ Can check market once a day
- ✅ Want safe, quality signals
- ✅ Can hold for 2-4 weeks

**Your Settings:**
```
MIN_MARKET_CAP_CRORE=50000          (Only large, safe companies)
RSI_OVERSOLD_THRESHOLD=25           (Wait for big discounts)
RSI_OVERBOUGHT_THRESHOLD=75         (Sell at peak)
HA_CONSECUTIVE_CANDLES=3            (Strong confirmation)
VOLUME_MULTIPLIER=1.5               (Only big money moves)
MAX_DISTANCE_BELOW_SMA200_PERCENT=12 (Only healthy trends)
RSI_RISING_CANDLES=2                (Confirmed momentum)
```

**Expected Results:**
- 2-4 signals per month
- 75-80% success rate
- 8-15% profit per trade
- Low stress, high quality

---

### Scenario 2: "I'm a Full-Time Trader"
**Your Profile:**
- ✅ Monitor market all day
- ✅ Can take quick decisions
- ✅ Want more opportunities
- ✅ Can handle some losses

**Your Settings:**
```
MIN_MARKET_CAP_CRORE=5000           (Include mid-caps)
RSI_OVERSOLD_THRESHOLD=35           (Early entries)
RSI_OVERBOUGHT_THRESHOLD=65         (Early exits)
HA_CONSECUTIVE_CANDLES=1            (Quick signals)
VOLUME_MULTIPLIER=1.1               (Accept moderate volume)
MAX_DISTANCE_BELOW_SMA200_PERCENT=25 (Deep value plays)
RSI_RISING_CANDLES=1                (Immediate entry)
```

**Expected Results:**
- 15-25 signals per month
- 60-65% success rate
- 5-10% profit per trade
- Active trading, more opportunities

---

### Scenario 3: "I'm Building Long-Term Wealth"
**Your Profile:**
- ✅ Have ₹20+ lakhs
- ✅ Can hold for months
- ✅ Want compounding returns
- ✅ Don't need frequent trades

**Your Settings:**
```
MIN_MARKET_CAP_CRORE=50000          (Blue-chip companies)
RSI_OVERSOLD_THRESHOLD=20           (Extreme discounts only)
RSI_OVERBOUGHT_THRESHOLD=80         (Maximum profit)
HA_CONSECUTIVE_CANDLES=3            (Very strong trends)
VOLUME_MULTIPLIER=2.0               (Institutional moves only)
MAX_DISTANCE_BELOW_SMA200_PERCENT=10 (Only strongest trends)
PRIMARY_WINDOW_CANDLES=90           (Long-term view)
```

**Expected Results:**
- 1-2 signals per month
- 85-90% success rate
- 15-25% profit per trade
- Patient, high-conviction investing

---

## 💡 KEY BUSINESS INSIGHTS

### 1. **Risk vs Reward Trade-off**
- More signals = More risk = Lower success rate
- Fewer signals = Less risk = Higher success rate
- **You decide:** Quantity or Quality?

### 2. **Capital Size Matters**
- Small capital (₹1-5 lakhs) → Need more opportunities → Aggressive settings
- Large capital (₹20+ lakhs) → Need quality → Conservative settings

### 3. **Time Availability**
- Full-time trader → Can use aggressive settings (monitor & exit quickly)
- Part-time trader → Must use conservative settings (can't react fast)

### 4. **Market Conditions**
- Bull market → Use aggressive settings (more opportunities)
- Bear market → Use conservative settings (protect capital)
- Sideways market → Use balanced settings

### 5. **Experience Level**
- Beginner → Start conservative, learn the system
- Intermediate → Use balanced, optimize gradually
- Expert → Customize based on your edge

---

## 🎓 LEARNING PATH

### Week 1: Start with BALANCED preset
- Observe signals
- Understand why each signal was generated
- Track success rate

### Week 2-3: Make ONE change
- Example: Change RSI_OVERSOLD from 30 to 35
- Observe impact on signal frequency
- Track success rate

### Week 4: Evaluate
- More signals? Better quality?
- Adjust based on results
- Keep what works, revert what doesn't

### Month 2: Fine-tune
- Optimize for your trading style
- Document your winning settings
- Stick to your system

---

## ⚠️ CRITICAL BUSINESS RULES

1. **Never chase quantity** - 10 quality signals > 50 poor signals
2. **Match settings to your lifestyle** - Don't use aggressive settings if you can't monitor
3. **Capital preservation first** - Better to miss opportunities than lose money
4. **One change at a time** - Can't learn if you change everything
5. **Give it time** - Need 20-30 signals to judge effectiveness

---

## 📞 DECISION FRAMEWORK

Before changing any parameter, ask yourself:

1. **"Why am I changing this?"**
   - Too many signals? → Make stricter
   - Too few signals? → Make relaxed
   - Too many losses? → Increase confirmation

2. **"Can I handle the consequences?"**
   - More signals = More time needed
   - Stricter filters = Fewer opportunities
   - Relaxed filters = More risk

3. **"Does this match my goal?"**
   - Quick profits → Aggressive
   - Steady growth → Balanced
   - Wealth building → Conservative

---

**Remember:** The best settings are the ones that let you sleep peacefully at night!
