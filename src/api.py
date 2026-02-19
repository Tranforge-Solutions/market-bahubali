from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from contextlib import asynccontextmanager
import os
import logging
from datetime import datetime

from src.database.db import db_instance
from src.models.models import Symbol, TradeSignal, Order, PaperTrade, Subscriber

logger = logging.getLogger(__name__)

# Simple job status tracking
job_status = {
    "last_run": None,
    "status": "idle",
    "message": "No jobs run yet"
}

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

class PaperTradeOut(BaseModel):
    id: int
    ticker: str
    entry_price: float
    exit_price: Optional[float]
    quantity: int
    stop_loss: Optional[float]
    target_price: Optional[float]
    status: str
    pnl: Optional[float]
    pnl_percent: Optional[float]
    entry_time: datetime
    exit_time: Optional[datetime]
    
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

@app.post("/run-job")
def run_job(background_tasks: BackgroundTasks):
    """Trigger the market scan job manually or via webhook."""
    def run_scan_task():
        global job_status
        try:
            job_status["status"] = "running"
            job_status["message"] = "Market scan in progress..."
            job_status["last_run"] = datetime.now()
            
            from src.main import run_scan
            logger.info("Starting background market scan...")
            run_scan()
            logger.info("Background market scan completed.")
            
            job_status["status"] = "completed"
            job_status["message"] = "Market scan completed successfully"
        except Exception as e:
            logger.error(f"Background scan failed: {e}")
            job_status["status"] = "failed"
            job_status["message"] = f"Market scan failed: {str(e)}"
    
    background_tasks.add_task(run_scan_task)
    return {"status": "success", "message": "Market scan triggered and running in background."}

@app.get("/job-status")
def get_job_status():
    """Get the status of the last background job."""
    return job_status

@app.post("/test-job")
def test_job():
    return {"status": "success", "message": "Test job triggered."}

@app.get("/health")
def health_check():
    """Check if the API and database are working."""
    try:
        db = db_instance.SessionLocal()
        symbol_count = db.query(Symbol).count()
        signal_count = db.query(TradeSignal).count()
        db.close()
        return {
            "status": "healthy",
            "database": "connected",
            "symbols": symbol_count,
            "signals": signal_count
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

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

@app.get("/paper-trades", response_model=List[PaperTradeOut])
def get_paper_trades(status: Optional[str] = None, limit: int = 50, db: Session = Depends(get_db_session)):
    """Get paper trades with optional status filter"""
    query = db.query(PaperTrade).join(Symbol)
    
    if status:
        query = query.filter(PaperTrade.status == status)
    
    trades = query.order_by(PaperTrade.entry_time.desc()).limit(limit).all()
    
    result = []
    for t in trades:
        result.append(PaperTradeOut(
            id=t.id,
            ticker=t.symbol.ticker,
            entry_price=t.entry_price,
            exit_price=t.exit_price,
            quantity=t.quantity,
            stop_loss=t.stop_loss,
            target_price=t.target_price,
            status=t.status,
            pnl=t.pnl,
            pnl_percent=t.pnl_percent,
            entry_time=t.entry_time,
            exit_time=t.exit_time
        ))
    return result

@app.get("/paper-trades/stats")
def get_paper_trade_stats(db: Session = Depends(get_db_session)):
    """Get paper trading statistics"""
    from sqlalchemy import func
    
    total_trades = db.query(PaperTrade).count()
    open_trades = db.query(PaperTrade).filter(PaperTrade.status == "OPEN").count()
    closed_trades = db.query(PaperTrade).filter(PaperTrade.status == "CLOSED").count()
    
    # Calculate win rate and avg P&L for closed trades
    closed_with_pnl = db.query(PaperTrade).filter(
        PaperTrade.status == "CLOSED",
        PaperTrade.pnl.isnot(None)
    ).all()
    
    if closed_with_pnl:
        winning_trades = len([t for t in closed_with_pnl if t.pnl > 0])
        win_rate = (winning_trades / len(closed_with_pnl)) * 100
        avg_pnl = sum([t.pnl for t in closed_with_pnl]) / len(closed_with_pnl)
        avg_pnl_percent = sum([t.pnl_percent for t in closed_with_pnl]) / len(closed_with_pnl)
    else:
        win_rate = 0
        avg_pnl = 0
        avg_pnl_percent = 0
    
    return {
        "total_trades": total_trades,
        "open_trades": open_trades,
        "closed_trades": closed_trades,
        "win_rate": round(win_rate, 2),
        "avg_pnl": round(avg_pnl, 2),
        "avg_pnl_percent": round(avg_pnl_percent, 2)
    }
