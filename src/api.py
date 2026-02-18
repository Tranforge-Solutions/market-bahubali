from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from contextlib import asynccontextmanager
import os
import logging

from src.database.db import db_instance
from src.models.models import Symbol, TradeSignal, Order

logger = logging.getLogger(__name__)

# Define Pydantic Models for Response
class SymbolOut(BaseModel):
    id: int
    ticker: str
    name: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True

class SignalOut(BaseModel):
    id: int
    symbol_ticker: str
    direction: str
    score: float
    confidence: str
    rsi: float
    price: float
    timestamp: datetime
    reasons: List[str] = []
    
    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    ticker: str
    action: str
    quantity: int
    price: float
    status: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize DB tables on startup."""
    logger.info("Starting up: initializing database tables...")
    db_instance.create_tables()
    logger.info("Database tables ready.")
    yield
    logger.info("Shutting down.")

app = FastAPI(title="Market Monitor API", lifespan=lifespan)

def get_db_session():
    db = db_instance.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"status": "online", "system": "Market Monitor"}

@app.get("/symbols", response_model=List[SymbolOut])
def get_symbols(db: Session = Depends(get_db_session)):
    return db.query(Symbol).filter(Symbol.is_active == True).all()

@app.get("/signals", response_model=List[SignalOut])
def get_signals(limit: int = 50, db: Session = Depends(get_db_session)):
    # Join with Symbol to get ticker
    signals = db.query(TradeSignal).join(Symbol).order_by(TradeSignal.generated_at.desc()).limit(limit).all()
    
    result = []
    for s in signals:
        # Use 'entry_price' from model, might be null if not set, fallback to 0.0
        price = s.entry_price if s.entry_price else 0.0
        
        # Regenerate Reasons dynamically
        reasons = []
        if s.direction == "LONG":
            if s.rsi < 30: reasons.append(f"Oversold (RSI: {s.rsi:.1f})")
            if s.score > 50: reasons.append("Bullish Trend Confirmation")
            reasons.append("Strategy: Dip Buy")
        else:
             if s.rsi > 70: reasons.append(f"Overbought (RSI: {s.rsi:.1f})")
             if s.score > 50: reasons.append("Bearish Trend Confirmation")
             reasons.append("Strategy: Top Sell")

        result.append(SignalOut(
            id=s.id,
            symbol_ticker=s.symbol.ticker,
            direction=s.direction,
            score=s.score,
            confidence=s.confidence,
            rsi=s.rsi,
            price=price,
            timestamp=s.generated_at,
            reasons=reasons
        ))
    return result

@app.get("/orders", response_model=List[OrderOut])
def get_orders(limit: int = 50, db: Session = Depends(get_db_session)):
    orders = db.query(Order).join(Symbol).order_by(Order.timestamp.desc()).limit(limit).all()
    
    result = []
    for o in orders:
        result.append(OrderOut(
            id=o.id,
            ticker=o.symbol.ticker,
            action=o.action,
            quantity=o.quantity,
            price=o.price,
            status=o.status,
            timestamp=o.timestamp
        ))
    return result
