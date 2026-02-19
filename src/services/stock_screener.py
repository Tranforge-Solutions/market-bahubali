"""
Indian Large-Cap Stock Screener
Implements screening logic based on RSI oversold + Heikin Ashi reversal strategy
"""

import logging
from typing import List, Dict, Any
import pandas as pd
from sqlalchemy.orm import Session
from src.models.models import Symbol, TradeSignal
from src.services.market_data import MarketDataService
from src.services.indicators import IndicatorService

logger = logging.getLogger(__name__)


class StockScreener:
    def __init__(self, db: Session):
        self.db = db
        self.market_data_service = MarketDataService(db)
        self.indicator_service = IndicatorService(db)
    
    def screen_large_cap_stocks(self, min_market_cap_cr: float = 100000) -> List[Dict[str, Any]]:
        """
        Screen Indian large-cap stocks based on Claude prompt criteria
        
        Core Conditions:
        1. RSI (14-day) between 20-35 (oversold)
        2. Recent Heikin-Ashi candle is green (bullish reversal)
        
        Additional Filters:
        3. Price above 200-day SMA (long-term uptrend)
        4. MACD bullish momentum
        5. Volume above 20-day average
        6. Bullish candlestick pattern
        """
        qualifying_stocks = []
        
        # Get large-cap symbols (market cap > specified threshold)
        symbols = self.db.query(Symbol).filter(
            Symbol.is_active.is_(True),
            Symbol.market_cap_cr >= min_market_cap_cr
        ).all()
        
        logger.info(f"Screening {len(symbols)} large-cap stocks (market cap > ₹{min_market_cap_cr:,.0f} Cr)")
        
        for symbol in symbols:
            try:
                # Load data with indicators
                df = self.indicator_service.load_data(symbol.ticker)
                if df.empty or len(df) < 200:  # Need 200 days for SMA200
                    continue
                
                df = self.indicator_service.calculate_indicators(df)
                latest = df.iloc[-1]
                
                # Core Condition 1: RSI between 20-35
                rsi = latest['RSI']
                if not (20 <= rsi <= 35):
                    continue
                
                # Core Condition 2: Green Heikin-Ashi candle
                ha_bullish = latest['HA_Close'] > latest['HA_Open']
                if not ha_bullish:
                    continue
                
                # Additional Filter 1: Price above 200-day SMA
                sma200 = df['close'].rolling(200).mean().iloc[-1]
                price_above_sma200 = latest['close'] > sma200
                
                # Additional Filter 2: MACD bullish momentum
                macd_bullish = self._check_macd_bullish(df)
                
                # Additional Filter 3: Volume above 20-day average
                vol_avg_20 = df['volume'].rolling(20).mean().iloc[-1]
                high_volume = latest['volume'] > vol_avg_20
                
                # Additional Filter 4: Bullish candlestick pattern
                bullish_pattern = self._check_bullish_pattern(df)
                
                # Calculate score based on conditions met
                conditions_met = {
                    'rsi_oversold': True,  # Already filtered
                    'ha_green': True,      # Already filtered
                    'above_sma200': price_above_sma200,
                    'macd_bullish': macd_bullish,
                    'high_volume': high_volume,
                    'bullish_pattern': bullish_pattern
                }
                
                # Only include stocks that meet core conditions
                score = sum(conditions_met.values()) * 100 // len(conditions_met)
                
                stock_data = {
                    'ticker': symbol.ticker,
                    'name': symbol.name,
                    'sector': symbol.sector,
                    'market_cap_cr': symbol.market_cap_cr,
                    'price': latest['close'],
                    'rsi': rsi,
                    'score': score,
                    'conditions_met': conditions_met,
                    'sma200': sma200,
                    'volume_ratio': latest['volume'] / vol_avg_20,
                    'ha_color': 'Green' if ha_bullish else 'Red',
                    'analysis_date': latest.name.strftime('%Y-%m-%d')
                }
                
                qualifying_stocks.append(stock_data)
                logger.info(f"✅ {symbol.ticker}: RSI={rsi:.1f}, Score={score}")
                
            except Exception as e:
                logger.error(f"Error screening {symbol.ticker}: {e}")
                continue
        
        # Sort by score descending
        qualifying_stocks.sort(key=lambda x: x['score'], reverse=True)
        
        logger.info(f"Found {len(qualifying_stocks)} qualifying large-cap stocks")
        return qualifying_stocks
    
    def _check_macd_bullish(self, df: pd.DataFrame) -> bool:
        """Check if MACD shows bullish momentum"""
        if len(df) < 26:  # Need enough data for MACD
            return False
        
        # Calculate MACD
        ema12 = df['close'].ewm(span=12).mean()
        ema26 = df['close'].ewm(span=26).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9).mean()
        
        latest_macd = macd_line.iloc[-1]
        latest_signal = signal_line.iloc[-1]
        prev_macd = macd_line.iloc[-2]
        prev_signal = signal_line.iloc[-2]
        
        # MACD crossed above signal OR both above zero
        bullish_cross = (latest_macd > latest_signal) and (prev_macd <= prev_signal)
        both_positive = (latest_macd > 0) and (latest_signal > 0)
        
        return bullish_cross or both_positive
    
    def _check_bullish_pattern(self, df: pd.DataFrame) -> bool:
        """Check for bullish candlestick patterns"""
        if len(df) < 2:
            return False
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Hammer pattern
        body = abs(latest['close'] - latest['open'])
        lower_shadow = latest['open'] - latest['low'] if latest['close'] > latest['open'] else latest['close'] - latest['low']
        upper_shadow = latest['high'] - max(latest['open'], latest['close'])
        
        hammer = (lower_shadow > 2 * body) and (upper_shadow < body)
        
        # Bullish engulfing
        prev_bearish = prev['close'] < prev['open']
        curr_bullish = latest['close'] > latest['open']
        engulfing = (prev_bearish and curr_bullish and 
                    latest['close'] > prev['open'] and 
                    latest['open'] < prev['close'])
        
        return hammer or engulfing
    
    def format_screening_results(self, results: List[Dict[str, Any]]) -> str:
        """Format screening results for display"""
        if not results:
            return "❌ No stocks found matching the screening criteria."
        
        msg = f"🔍 <b>Large-Cap Stock Screening Results</b>\n"
        msg += f"📊 Found {len(results)} qualifying stocks\n\n"
        
        for i, stock in enumerate(results[:10], 1):  # Top 10
            conditions = stock['conditions_met']
            
            # Build condition summary
            met_conditions = []
            if conditions['rsi_oversold']:
                met_conditions.append(f"RSI: {stock['rsi']:.1f} (Oversold)")
            if conditions['ha_green']:
                met_conditions.append("HA: Green Candle")
            if conditions['above_sma200']:
                met_conditions.append("Above SMA200")
            if conditions['macd_bullish']:
                met_conditions.append("MACD: Bullish")
            if conditions['high_volume']:
                met_conditions.append(f"Volume: {stock['volume_ratio']:.1f}x avg")
            if conditions['bullish_pattern']:
                met_conditions.append("Bullish Pattern")
            
            msg += (
                f"{i}. <b>{stock['ticker']}</b> - {stock['name']}\n"
                f"   💰 Price: ₹{stock['price']:.2f} | Score: {stock['score']}/100\n"
                f"   🏭 Sector: {stock['sector']} | Cap: ₹{stock['market_cap_cr']:,.0f} Cr\n"
                f"   ✅ Conditions: {', '.join(met_conditions)}\n\n"
            )
        
        msg += f"<i>Analysis Date: {results[0]['analysis_date']}</i>"
        return msg