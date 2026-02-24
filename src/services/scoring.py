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
        Evaluates a single candle (row) against scoring rules using dual window approach.
        Primary logic: last 3 months (60-70 candles)
        Confirmation: last 20-30 candles
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
        current_volume = row.get('volume', 0)

        # Calculate volume average if df is provided
        volume_above_avg = False
        if df is not None and len(df) >= Config.VOLUME_AVERAGE_PERIOD:
            current_idx = df.index.get_loc(row.name)
            if current_idx >= Config.VOLUME_AVERAGE_PERIOD:
                avg_volume = df['volume'].iloc[current_idx - Config.VOLUME_AVERAGE_PERIOD:current_idx].mean()
                if avg_volume > 0:
                    volume_above_avg = current_volume > (Config.VOLUME_MULTIPLIER * avg_volume)

        # Use dual window approach
        if df is not None and len(df) >= Config.PRIMARY_WINDOW_CANDLES:
            # Get primary window (last 70 candles) and confirmation window (last 30 candles)
            current_idx = df.index.get_loc(row.name)

            # Primary window for trend analysis
            primary_start = max(0, current_idx - Config.PRIMARY_WINDOW_CANDLES + 1)
            primary_df = df.iloc[primary_start:current_idx + 1]

            # Confirmation window for recent momentum
            confirmation_start = max(0, current_idx - Config.CONFIRMATION_WINDOW_CANDLES + 1)
            confirmation_df = df.iloc[confirmation_start:current_idx + 1]

        # Check RSI rising/falling trend using confirmation window
        rsi_rising = False
        rsi_falling = False

        # Check HA consecutive candles using confirmation window
        ha_bullish_confirmed = False
        ha_bearish_confirmed = False

        if df is not None and len(df) >= Config.PRIMARY_WINDOW_CANDLES:
            # Get primary window (last 70 candles) and confirmation window (last 30 candles)
            current_idx = df.index.get_loc(row.name)

            # Primary window for trend analysis
            primary_start = max(0, current_idx - Config.PRIMARY_WINDOW_CANDLES + 1)
            primary_df = df.iloc[primary_start:current_idx + 1]

            # Confirmation window for recent momentum
            confirmation_start = max(0, current_idx - Config.CONFIRMATION_WINDOW_CANDLES + 1)
            confirmation_df = df.iloc[confirmation_start:current_idx + 1]

            # Check RSI trend in confirmation window
            if len(confirmation_df) >= Config.RSI_RISING_CANDLES:
                rsi_values = confirmation_df['RSI'].tail(Config.RSI_RISING_CANDLES + 1).values
                rsi_rising = all(rsi_values[i] < rsi_values[i+1] for i in range(len(rsi_values)-1))
                rsi_falling = all(rsi_values[i] > rsi_values[i+1] for i in range(len(rsi_values)-1))

            # Check HA consecutive candles in confirmation window
            if len(confirmation_df) >= Config.HA_CONSECUTIVE_CANDLES:
                ha_green_values = confirmation_df['HA_Green'].tail(Config.HA_CONSECUTIVE_CANDLES).values
                ha_close_values = confirmation_df['HA_Close'].tail(Config.HA_CONSECUTIVE_CANDLES).values

                if len(ha_green_values) == Config.HA_CONSECUTIVE_CANDLES:
                    ha_bullish_confirmed = all(ha_green_values) and ha_close_values[-1] > ha_close_values[-2]
                    ha_bearish_confirmed = all(~ha_green_values) and ha_close_values[-1] < ha_close_values[-2]
        else:
            # Fallback to old logic if not enough data
            if df is not None and len(df) >= max(Config.RSI_RISING_CANDLES, Config.HA_CONSECUTIVE_CANDLES):
                current_idx = df.index.get_loc(row.name)

            # Fallback to old logic if not enough data
            if df is not None and len(df) >= max(Config.RSI_RISING_CANDLES, Config.HA_CONSECUTIVE_CANDLES):
                current_idx = df.index.get_loc(row.name)

                # Check if we have enough previous candles
                if current_idx >= Config.RSI_RISING_CANDLES:
                    # Get RSI values for last N candles including current
                    rsi_values = df['RSI'].iloc[current_idx - Config.RSI_RISING_CANDLES:current_idx + 1].values

                    # Check if RSI is consistently rising
                    rsi_rising = all(rsi_values[i] < rsi_values[i+1] for i in range(len(rsi_values)-1))

                    # Check if RSI is consistently falling
                    rsi_falling = all(rsi_values[i] > rsi_values[i+1] for i in range(len(rsi_values)-1))

                # Check HA consecutive candles
                if current_idx >= Config.HA_CONSECUTIVE_CANDLES:
                    # Get last N HA candles including current
                    ha_green_values = df['HA_Green'].iloc[current_idx - Config.HA_CONSECUTIVE_CANDLES + 1:current_idx + 1].values
                    ha_close_values = df['HA_Close'].iloc[current_idx - Config.HA_CONSECUTIVE_CANDLES + 1:current_idx + 1].values

                    # Check for consecutive green candles AND current close > previous close
                    if len(ha_green_values) == Config.HA_CONSECUTIVE_CANDLES:
                        ha_bullish_confirmed = all(ha_green_values) and ha_close_values[-1] > ha_close_values[-2]

                        # Check for consecutive red candles AND current close < previous close
                        ha_bearish_confirmed = all(~ha_green_values) and ha_close_values[-1] < ha_close_values[-2]

        # ---------------------------
        # LONG Logic (Buying the Dip)
        # ---------------------------
        # Check RSI oversold condition (skip if RSI_OVERSOLD_THRESHOLD is NA)
        rsi_oversold_check = Config.RSI_OVERSOLD_THRESHOLD is None or rsi < Config.RSI_OVERSOLD_THRESHOLD
        rsi_rising_check = Config.RSI_RISING_CANDLES is None or rsi_rising
        
        if rsi_oversold_check and rsi_rising_check:
            # Trend Damage Check (skip if MAX_DISTANCE_BELOW_SMA200_PERCENT is NA)
            if Config.MAX_DISTANCE_BELOW_SMA200_PERCENT is not None and sma200 > 0:
                distance_below_pct = ((sma200 - close) / sma200) * 100
                if distance_below_pct > Config.MAX_DISTANCE_BELOW_SMA200_PERCENT:
                    long_reasons.append(f"⚠️ Trend Damaged: Price {distance_below_pct:.1f}% below 200 SMA (Max: {Config.MAX_DISTANCE_BELOW_SMA200_PERCENT}%)")
                    # Skip this signal - trend is too damaged
                    pass
                else:
                    long_score += self.SCORE_RSI_EXTREME
                    if Config.RSI_OVERSOLD_THRESHOLD is not None:
                        long_reasons.append(f"Oversold & Rising RSI (RSI: {rsi:.1f}, Rising for {Config.RSI_RISING_CANDLES or 'any'} candles)")
                    else:
                        long_reasons.append(f"Rising RSI Momentum (RSI: {rsi:.1f})")

                    # Heikin Ashi Confirmation (skip if HA_CONSECUTIVE_CANDLES is NA)
                    if Config.HA_CONSECUTIVE_CANDLES is None or ha_bullish_confirmed:
                        long_score += self.SCORE_TREND_CONFIRM
                        if Config.HA_CONSECUTIVE_CANDLES is not None:
                            long_reasons.append(f"Bullish Momentum Confirmed ({Config.HA_CONSECUTIVE_CANDLES} Green HA Candles, Close Rising)")
                        else:
                            long_reasons.append("Bullish Momentum (HA filter skipped)")

                    # Volume Check (skip if VOLUME_MULTIPLIER is NA)
                    if Config.VOLUME_MULTIPLIER is None:
                        long_score += self.SCORE_VOL_MED
                        long_reasons.append("Volume filter skipped")
                    elif volume_above_avg:
                        long_score += self.SCORE_VOL_HIGH
                        long_reasons.append(f"High Volume Conviction (>{Config.VOLUME_MULTIPLIER}x {Config.VOLUME_AVERAGE_PERIOD}-day avg)")
                    elif vol_z > 1.0:
                        long_score += self.SCORE_VOL_MED
                        long_reasons.append(f"Moderate Volume (Z-Score: {vol_z:.1f})")

                    # Trend Filter (Are we in a general uptrend?)
                    if close > sma200:
                        long_score += self.SCORE_SMA_FILTER
                        long_reasons.append("Major Uptrend Support (> 200 SMA)")
            else:
                # No SMA200 data or filter skipped, proceed
                long_score += self.SCORE_RSI_EXTREME
                if Config.RSI_OVERSOLD_THRESHOLD is not None:
                    long_reasons.append(f"Oversold & Rising RSI (RSI: {rsi:.1f}, Rising for {Config.RSI_RISING_CANDLES or 'any'} candles)")
                else:
                    long_reasons.append(f"Rising RSI Momentum (RSI: {rsi:.1f})")

                # Heikin Ashi Confirmation (skip if HA_CONSECUTIVE_CANDLES is NA)
                if Config.HA_CONSECUTIVE_CANDLES is None or ha_bullish_confirmed:
                    long_score += self.SCORE_TREND_CONFIRM
                    if Config.HA_CONSECUTIVE_CANDLES is not None:
                        long_reasons.append(f"Bullish Momentum Confirmed ({Config.HA_CONSECUTIVE_CANDLES} Green HA Candles, Close Rising)")
                    else:
                        long_reasons.append("Bullish Momentum (HA filter skipped)")

                # Volume Check (skip if VOLUME_MULTIPLIER is NA)
                if Config.VOLUME_MULTIPLIER is None:
                    long_score += self.SCORE_VOL_MED
                    long_reasons.append("Volume filter skipped")
                elif volume_above_avg:
                    long_score += self.SCORE_VOL_HIGH
                    long_reasons.append(f"High Volume Conviction (>{Config.VOLUME_MULTIPLIER}x {Config.VOLUME_AVERAGE_PERIOD}-day avg)")

        # ---------------------------
        # SHORT Logic (Selling the Top)
        # ---------------------------
        # Check RSI overbought condition (skip if RSI_OVERBOUGHT_THRESHOLD is NA)
        rsi_overbought_check = Config.RSI_OVERBOUGHT_THRESHOLD is None or rsi > Config.RSI_OVERBOUGHT_THRESHOLD
        rsi_falling_check = Config.RSI_FALLING_CANDLES is None or rsi_falling
        
        if rsi_overbought_check and rsi_falling_check:
            short_score += self.SCORE_RSI_EXTREME
            if Config.RSI_OVERBOUGHT_THRESHOLD is not None:
                short_reasons.append(f"Overbought & Falling RSI (RSI: {rsi:.1f}, Falling for {Config.RSI_FALLING_CANDLES or 'any'} candles)")
            else:
                short_reasons.append(f"Falling RSI Momentum (RSI: {rsi:.1f})")

            # Heikin Ashi Confirmation (skip if HA_CONSECUTIVE_CANDLES is NA)
            if Config.HA_CONSECUTIVE_CANDLES is None or ha_bearish_confirmed:
                short_score += self.SCORE_TREND_CONFIRM
                if Config.HA_CONSECUTIVE_CANDLES is not None:
                    short_reasons.append(f"Bearish Momentum Confirmed ({Config.HA_CONSECUTIVE_CANDLES} Red HA Candles, Close Falling)")
                else:
                    short_reasons.append("Bearish Momentum (HA filter skipped)")

            # Volume Check (skip if VOLUME_MULTIPLIER is NA)
            if Config.VOLUME_MULTIPLIER is None:
                short_score += self.SCORE_VOL_MED
                short_reasons.append("Volume filter skipped")
            elif volume_above_avg:
                short_score += self.SCORE_VOL_HIGH
                short_reasons.append(f"High Volume Conviction (>{Config.VOLUME_MULTIPLIER}x {Config.VOLUME_AVERAGE_PERIOD}-day avg)")
            elif vol_z > 1.0:
                short_score += self.SCORE_VOL_MED
                short_reasons.append(f"Moderate Volume (Z-Score: {vol_z:.1f})")

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
