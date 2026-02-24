from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database.db import Base
import datetime

class Symbol(Base):
    __tablename__ = "symbols"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    sector = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    market_cap_cr = Column(Float, nullable=True)  # Market cap in crores
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    ohlcv_data = relationship("OHLCV", back_populates="symbol")
    signals = relationship("TradeSignal", back_populates="symbol")

class OHLCV(Base):
    __tablename__ = "ohlcv"

    id = Column(Integer, primary_key=True, index=True)
    symbol_id = Column(Integer, ForeignKey("symbols.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)

    symbol = relationship("Symbol", back_populates="ohlcv_data")

class TradeSignal(Base):
    __tablename__ = "trade_signals"

    id = Column(Integer, primary_key=True, index=True)
    symbol_id = Column(Integer, ForeignKey("symbols.id"), nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Analysis Data
    rsi = Column(Float)
    atr = Column(Float)
    score = Column(Float)
    confidence = Column(String) # High, Medium, Low

    # Trade Setup
    direction = Column(String) # LONG / SHORT
    entry_price = Column(Float)
    stop_loss = Column(Float)
    target_1 = Column(Float)
    target_2 = Column(Float)

    symbol = relationship("Symbol", back_populates="signals")

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    symbol_id = Column(Integer, ForeignKey('symbols.id'))
    action = Column(String) # BUY/SELL
    quantity = Column(Integer)
    price = Column(Float)
    status = Column(String, default="PENDING") # PENDING, EXECUTED
    timestamp = Column(DateTime, default=func.now())

    symbol = relationship("Symbol")

class Subscriber(Base):
    __tablename__ = 'subscribers'

    id = Column(Integer, primary_key=True)
    chat_id = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    joined_at = Column(DateTime, default=func.now())

    trades = relationship("PaperTrade", back_populates="subscriber")

class PaperTrade(Base):
    __tablename__ = 'paper_trades'

    id = Column(Integer, primary_key=True)
    subscriber_id = Column(Integer, ForeignKey('subscribers.id'), nullable=False)
    signal_id = Column(Integer, ForeignKey('trade_signals.id'), nullable=False)
    symbol_id = Column(Integer, ForeignKey('symbols.id'), nullable=False)

    # Entry Details
    entry_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    order_type = Column(String, default="MARKET")  # MARKET, LIMIT

    # Risk Management
    stop_loss = Column(Float)
    target_price = Column(Float)
    auto_exit = Column(Boolean, default=False)

    # Exit Details
    exit_price = Column(Float)
    exit_reason = Column(String)  # MANUAL, TARGET, STOPLOSS, AUTO

    # Trade Status
    status = Column(String, default="OPEN")  # OPEN, CLOSED, EXPIRED

    # Timestamps
    entry_time = Column(DateTime, default=func.now())
    exit_time = Column(DateTime)

    # P&L
    pnl = Column(Float)
    pnl_percent = Column(Float)

    # Relationships
    subscriber = relationship("Subscriber", back_populates="trades")
    signal = relationship("TradeSignal")
    symbol = relationship("Symbol")
