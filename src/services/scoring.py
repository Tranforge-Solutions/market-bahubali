import pandas as pd
from typing import Dict, Any
from src.config.settings import Config

class ScoringService:
    """
    Implements a weighted rule-based scoring engine for trade setups.
    
    Strategy: 'Dip Buying in Uptrend'
    - Primary Driver: RSI Oversold (Mean Reversion)
    - Filter: SMA Trend Alignment (Trade with the trend)
    - Confirmation: Volume Spike
    """

    # Scoring Weights & Thresholds
    SCORE_RSI_EXTREME = 40       # RSI < 35 (Buy) or RSI > 70 (Sell)
    SCORE_TREND_CONFIRM = 20     # HA Color matches direction
    SCORE_VOL_HIGH = 15          # Z-Score > 2.0
    SCORE_VOL_MED = 10           # Z-Score > 1.0
    SCORE_SMA_FILTER = 10        # Above/Below 200 SMA (Filter)

    # Classifications
    CONFIDENCE_HIGH = 70
    CONFIDENCE_MED = 50
    CONFIDENCE_LOW = 30

    def score_signal(self, row: pd.Series, df: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Evaluates a single candle (row) against scoring rules.
        Returns a dictionary with score, confidence, direction, and reasoning.
        """
        long_score = 0
        short_score = 0
        long_reasons = []
        short_reasons = []
        
        rsi = row.get('RSI', 50)
        ha_green = row.get('HA_Green', None) # True if Green, False if Red
        vol_z = row.get('Vol_Z', 0)
        close = row['close']
        sma200 = row.get('SMA_200', 0)
        
        # Check RSI rising/falling trend
        rsi_rising = False
        rsi_falling = False
        
        if df is not None and len(df) >= Config.RSI_RISING_CANDLES:
            # Get the index of current row
            current_idx = df.index.get_loc(row.name)
            
            # Check if we have enough previous candles
            if current_idx >= Config.RSI_RISING_CANDLES:
                # Get RSI values for last N candles including current
                rsi_values = df['RSI'].iloc[current_idx - Config.RSI_RISING_CANDLES:current_idx + 1].values
                
                # Check if RSI is consistently rising
                rsi_rising = all(rsi_values[i] < rsi_values[i+1] for i in range(len(rsi_values)-1))
                
                # Check if RSI is consistently falling
                rsi_falling = all(rsi_values[i] > rsi_values[i+1] for i in range(len(rsi_values)-1))

        # ---------------------------
        # LONG Logic (Buying the Dip)
        # ---------------------------
        if rsi < Config.RSI_OVERSOLD_THRESHOLD and rsi_rising:
            long_score += self.SCORE_RSI_EXTREME
            long_reasons.append(f"Oversold & Rising RSI (RSI: {rsi:.1f}, Rising for {Config.RSI_RISING_CANDLES} candles)")
            
            # Heikin Ashi Confirmation (Green implies reversal starting?)
            if ha_green: 
                long_score += self.SCORE_TREND_CONFIRM
                long_reasons.append("Bullish Momentum Reversal (Heikin Ashi)")
            
            # Volume Spike is good for reversal
            if vol_z > 2.0:
                long_score += self.SCORE_VOL_HIGH
                long_reasons.append(f"High Volume Conviction (Z-Score: {vol_z:.1f})")
            
            # Trend Filter (Are we in a general uptrend?)
            if sma200 > 0 and close > sma200:
                long_score += self.SCORE_SMA_FILTER
                long_reasons.append("Major Uptrend Support (> 200 SMA)")

        # ---------------------------
        # SHORT Logic (Selling the Top)
        # ---------------------------
        if rsi > Config.RSI_OVERBOUGHT_THRESHOLD and rsi_falling:
            short_score += self.SCORE_RSI_EXTREME
            short_reasons.append(f"Overbought & Falling RSI (RSI: {rsi:.1f}, Falling for {Config.RSI_FALLING_CANDLES} candles)")
            
            # Heikin Ashi Confirmation (Red implies weakness?)
            if not ha_green:
                short_score += self.SCORE_TREND_CONFIRM
                short_reasons.append("Bearish Momentum Reversal (Heikin Ashi)")

            # Volume Spike
            if vol_z > 2.0:
                short_score += self.SCORE_VOL_HIGH
                short_reasons.append(f"High Volume Conviction (Z-Score: {vol_z:.1f})")
                
            # Trend Filter (Are we in a general downtrend?)
            if sma200 > 0 and close < sma200:
                short_score += self.SCORE_SMA_FILTER
                short_reasons.append("Major Downtrend Resistance (< 200 SMA)")

        # ---------------------------
        # Final Decision
        # ---------------------------
        # Compare scores to see which side wins (if any)
        # Note: Usually RSI won't be <30 and >70 at same time, so mutually exclusive.
        
        final_score = 0
        direction = "NEUTRAL"
        reasons = []
        confidence = "No Trade"

        if long_score >= self.CONFIDENCE_LOW and long_score > short_score:
            final_score = long_score
            direction = "LONG"
            reasons = long_reasons
        elif short_score >= self.CONFIDENCE_LOW and short_score > long_score:
            final_score = short_score
            direction = "SHORT"
            reasons = short_reasons
            
        # Determine Confidence
        if final_score >= self.CONFIDENCE_HIGH:
            confidence = "High"
        elif final_score >= self.CONFIDENCE_MED:
            confidence = "Medium"
        elif final_score >= self.CONFIDENCE_LOW:
            confidence = "Low"

        return {
            "score": final_score,
            "confidence": confidence,
            "direction": direction,
            "reasons": reasons
        }
