from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from src.models.models import Symbol, OHLCV, TradeSignal
from datetime import datetime, timedelta
import pytz
import logging

logger = logging.getLogger(__name__)

class SymbolFilterService:
    """Pre-filter symbols at DB level to reduce evaluation load"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_filtered_symbols(self, min_data_days: int = 200):
        """
        Get symbols that meet basic criteria without loading full data:
        1. Has minimum data days
        2. Has recent price activity (last 7 days)
        """
        recent_date = datetime.now(pytz.UTC) - timedelta(days=7)
        
        # Subquery: Count data points per symbol
        data_count = self.db.query(
            OHLCV.symbol_id,
            func.count(OHLCV.id).label('data_count'),
            func.max(OHLCV.timestamp).label('last_update')
        ).group_by(OHLCV.symbol_id).subquery()
        
        # Main query: Get symbols with sufficient data and recent activity
        filtered_symbols = self.db.query(Symbol).join(
            data_count, Symbol.id == data_count.c.symbol_id
        ).filter(
            and_(
                Symbol.is_active == True,
                data_count.c.data_count >= min_data_days,
                data_count.c.last_update >= recent_date
            )
        ).all()
        
        # Debug: Check if specific symbol was filtered out
        all_active = self.db.query(Symbol).filter(Symbol.is_active == True).count()
        logger.info(f"Pre-filtered: {len(filtered_symbols)}/{all_active} symbols meet criteria (>={min_data_days} days data, updated in last 7 days)")
        
        # Check KANSAINER.NS specifically
        kansainer = self.db.query(Symbol).filter(Symbol.ticker == 'KANSAINER.NS').first()
        if kansainer:
            kans_data = self.db.query(
                func.count(OHLCV.id).label('count'),
                func.max(OHLCV.timestamp).label('last_update')
            ).filter(OHLCV.symbol_id == kansainer.id).first()
            logger.info(f"KANSAINER.NS: {kans_data.count} days, last update: {kans_data.last_update}")
        
        return filtered_symbols
    
    def get_symbols_by_recent_rsi(self, rsi_min: float = None, rsi_max: float = None):
        """
        Get symbols based on their most recent RSI signal
        Useful for finding oversold (RSI < 35) or overbought (RSI > 65) stocks
        """
        # Subquery: Get latest signal per symbol
        latest_signals = self.db.query(
            TradeSignal.symbol_id,
            func.max(TradeSignal.generated_at).label('latest_time')
        ).group_by(TradeSignal.symbol_id).subquery()
        
        # Join to get actual RSI values
        query = self.db.query(Symbol).join(
            TradeSignal, Symbol.id == TradeSignal.symbol_id
        ).join(
            latest_signals,
            and_(
                TradeSignal.symbol_id == latest_signals.c.symbol_id,
                TradeSignal.generated_at == latest_signals.c.latest_time
            )
        ).filter(Symbol.is_active == True)
        
        if rsi_min is not None:
            query = query.filter(TradeSignal.rsi >= rsi_min)
        if rsi_max is not None:
            query = query.filter(TradeSignal.rsi <= rsi_max)
        
        symbols = query.all()
        logger.info(f"Found {len(symbols)} symbols with RSI in range [{rsi_min}, {rsi_max}]")
        return symbols
