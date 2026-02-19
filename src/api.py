#!/usr/bin/env python3
"""
REST API for portfolio management and authentication
"""

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
import jwt
import random
import string
import logging
from sqlalchemy.orm import Session
from src.database.db import db_instance
from src.models.models import Subscriber, PaperTrade, Symbol, TradeSignal
from src.services.portfolio import PortfolioService
from src.services.alerting import AlertService
import os

logger = logging.getLogger(__name__)

# Simple job status tracking
job_status = {
    "last_run": None,
    "status": "idle",
    "message": "No jobs run yet"
}

app = FastAPI(
    title="Market Monitor Trading API",
    description="REST API for paper trading system with portfolio management and authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
security = HTTPBearer()


@app.get("/", summary="Health Check", description="API health check endpoint")
async def root():
    """Health check endpoint for deployment"""
    return {"status": "healthy", "message": "Market Monitor API is running"}


@app.get("/status", summary="System Status", description="Get system status and configuration")
async def get_status():
    """Get system status"""
    return {
        "status": "running",
        "version": "1.0.0",
        "environment": "production" if os.getenv("DATABASE_URL") else "development",
        "features": {
            "paper_trading": True,
            "telegram_bot": True,
            "auto_sell": True,
            "portfolio_tracking": True
        }
    }


@app.post("/run-job", summary="Trigger Market Scan", description="Manually trigger market scan job")
async def run_job(background_tasks: BackgroundTasks):
    """Trigger market scan job"""
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


@app.get("/job-status", summary="Get Job Status", description="Get the status of the last background job")
async def get_job_status():
    """Get the status of the last background job"""
    return job_status


@app.get("/health", summary="Health Check", description="Check if the API and database are working")
async def health_check(db: Session = Depends(get_db)):
    """Check if the API and database are working"""
    try:
        symbol_count = db.query(Symbol).count()
        signal_count = db.query(TradeSignal).count()
        return {
            "status": "healthy",
            "database": "connected",
            "symbols": symbol_count,
            "signals": signal_count
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.get("/symbols", summary="Get Active Symbols", description="Get list of active trading symbols")
async def get_symbols(db: Session = Depends(get_db)):
    """Get active symbols"""
    symbols = db.query(Symbol).filter(Symbol.is_active.is_(True)).all()
    return [{
        "id": s.id,
        "ticker": s.ticker,
        "name": s.name,
        "sector": s.sector,
        "industry": s.industry,
        "is_active": s.is_active
    } for s in symbols]


@app.get("/signals", summary="Get Trading Signals", description="Get recent trading signals")
async def get_signals(limit: int = 50, db: Session = Depends(get_db)):
    """Get recent trading signals"""
    signals = db.query(TradeSignal).join(Symbol).order_by(TradeSignal.generated_at.desc()).limit(limit).all()
    
    result = []
    for s in signals:
        result.append({
            "id": s.id,
            "symbol_ticker": s.symbol.ticker,
            "direction": s.direction,
            "score": s.score,
            "confidence": s.confidence,
            "rsi": s.rsi,
            "timestamp": s.generated_at
        })
    return result

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# In-memory OTP storage (use Redis in production)
otp_storage = {}

class LoginRequest(BaseModel):
    mobile: str = Field(..., description="Mobile number linked to telegram account", example="9876543210")

class VerifyOTPRequest(BaseModel):
    mobile: str = Field(..., description="Mobile number", example="9876543210")
    otp: str = Field(..., description="6-digit OTP received on telegram", example="123456")

class TradeFilter(BaseModel):
    status: Optional[str] = Field(None, description="Trade status filter", example="OPEN")
    symbol: Optional[str] = Field(None, description="Symbol filter", example="RELIANCE.NS")
    date_from: Optional[datetime] = Field(None, description="Start date filter")
    date_to: Optional[datetime] = Field(None, description="End date filter")

class TradeResponse(BaseModel):
    id: int
    symbol: str
    company_name: str
    entry_price: float
    exit_price: Optional[float]
    quantity: int
    pnl: Optional[float]
    pnl_percent: Optional[float]
    status: str
    entry_time: datetime
    exit_time: Optional[datetime]
    exit_reason: Optional[str]

class PortfolioResponse(BaseModel):
    total_pnl: float = Field(..., description="Total profit/loss in rupees")
    total_trades: int = Field(..., description="Total number of completed trades")
    winning_trades: int = Field(..., description="Number of profitable trades")
    losing_trades: int = Field(..., description="Number of loss-making trades")
    win_rate: float = Field(..., description="Win rate percentage")
    avg_pnl: float = Field(..., description="Average P&L per trade")
    open_positions: int = Field(..., description="Number of currently open trades")

def get_db():
    db = db_instance.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        chat_id: str = payload.get("sub")
        if chat_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return chat_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

@app.post("/auth/login", summary="Send OTP to Telegram", description="Send 6-digit OTP to user's telegram account for authentication")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Send OTP to user's telegram"""
    # Find subscriber by mobile (assuming mobile is stored in chat_id for now)
    subscriber = db.query(Subscriber).filter(Subscriber.chat_id.contains(request.mobile)).first()

    if not subscriber:
        raise HTTPException(status_code=404, detail="User not found. Please start the telegram bot first.")

    # Generate and store OTP
    otp = generate_otp()
    otp_storage[request.mobile] = {
        "otp": otp,
        "chat_id": subscriber.chat_id,
        "expires": datetime.utcnow() + timedelta(minutes=5)
    }

    # Send OTP via telegram
    alert_service = AlertService()
    msg = f"🔐 <b>Login OTP</b>\n\nYour OTP: <code>{otp}</code>\n\nValid for 5 minutes."
    alert_service.send_telegram_message(msg, specific_chat_id=subscriber.chat_id)

    return {"message": "OTP sent to your telegram"}

@app.post("/auth/verify-otp", summary="Verify OTP and get JWT token", description="Verify the OTP received on telegram and get JWT access token")
async def verify_otp(request: VerifyOTPRequest):
    """Verify OTP and return JWT token"""
    stored_data = otp_storage.get(request.mobile)

    if not stored_data:
        raise HTTPException(status_code=400, detail="OTP not found or expired")

    if datetime.utcnow() > stored_data["expires"]:
        del otp_storage[request.mobile]
        raise HTTPException(status_code=400, detail="OTP expired")

    if stored_data["otp"] != request.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Generate JWT token
    access_token = create_access_token(data={"sub": stored_data["chat_id"]})

    # Clean up OTP
    del otp_storage[request.mobile]

    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/portfolio", response_model=PortfolioResponse, summary="Get Portfolio Summary", description="Get complete portfolio performance summary for authenticated user")
async def get_portfolio(chat_id: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Get user portfolio summary"""
    portfolio_service = PortfolioService(db)
    portfolio = portfolio_service.get_user_portfolio(chat_id)

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    return PortfolioResponse(
        total_pnl=portfolio["total_pnl"],
        total_trades=portfolio["total_trades"],
        winning_trades=portfolio["winning_trades"],
        losing_trades=portfolio["losing_trades"],
        win_rate=portfolio["win_rate"],
        avg_pnl=portfolio["avg_pnl"],
        open_positions=len(portfolio["open_trades"])
    )

@app.get("/trades", response_model=List[TradeResponse], summary="Get Trade History", description="Get user's trade history with optional filters")
async def get_trades(
    status: Optional[str] = None,
    symbol: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    chat_id: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get user trades with filters"""
    subscriber = db.query(Subscriber).filter(Subscriber.chat_id == chat_id).first()
    if not subscriber:
        raise HTTPException(status_code=404, detail="User not found")

    query = db.query(PaperTrade).filter(PaperTrade.subscriber_id == subscriber.id)

    # Apply filters
    if status:
        query = query.filter(PaperTrade.status == status.upper())
    if symbol:
        symbol_obj = db.query(Symbol).filter(Symbol.ticker == symbol.upper()).first()
        if symbol_obj:
            query = query.filter(PaperTrade.symbol_id == symbol_obj.id)
    if date_from:
        query = query.filter(PaperTrade.entry_time >= date_from)
    if date_to:
        query = query.filter(PaperTrade.entry_time <= date_to)

    trades = query.order_by(PaperTrade.entry_time.desc()).all()

    result = []
    for trade in trades:
        symbol_obj = db.query(Symbol).filter(Symbol.id == trade.symbol_id).first()
        result.append(TradeResponse(
            id=trade.id,
            symbol=symbol_obj.ticker,
            company_name=symbol_obj.name or "N/A",
            entry_price=trade.entry_price,
            exit_price=trade.exit_price,
            quantity=trade.quantity,
            pnl=trade.pnl,
            pnl_percent=trade.pnl_percent,
            status=trade.status,
            entry_time=trade.entry_time,
            exit_time=trade.exit_time,
            exit_reason=trade.exit_reason
        ))

    return result

@app.get("/leaderboard", summary="Get Leaderboard", description="Get top 10 performers leaderboard (privacy-masked)")
async def get_leaderboard(db: Session = Depends(get_db)):
    """Get top performers leaderboard"""
    portfolio_service = PortfolioService(db)
    leaders = portfolio_service.get_leaderboard(10)

    result = []
    for i, leader in enumerate(leaders, 1):
        win_rate = (leader.wins / leader.trade_count * 100) if leader.trade_count > 0 else 0
        result.append({
            "rank": i,
            "user_id": f"***{leader.chat_id[-4:]}",  # Masked for privacy
            "total_pnl": float(leader.total_pnl),
            "trade_count": leader.trade_count,
            "wins": leader.wins,
            "win_rate": round(win_rate, 1)
        })

    return result

@app.post("/trades/{trade_id}/sell", summary="Manual Sell Trade", description="Manually close an open trade at current market price")
async def manual_sell(
    trade_id: int,
    chat_id: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Manually sell a trade"""
    subscriber = db.query(Subscriber).filter(Subscriber.chat_id == chat_id).first()
    if not subscriber:
        raise HTTPException(status_code=404, detail="User not found")

    trade = db.query(PaperTrade).filter(
        PaperTrade.id == trade_id,
        PaperTrade.subscriber_id == subscriber.id,
        PaperTrade.status == "OPEN"
    ).first()

    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found or already closed")

    # Get current price and close trade
    from src.services.auto_sell import AutoSellService
    auto_sell_service = AutoSellService()
    symbol = db.query(Symbol).filter(Symbol.id == trade.symbol_id).first()
    current_price = auto_sell_service.get_current_price(symbol.ticker)

    if not current_price:
        raise HTTPException(status_code=400, detail="Unable to fetch current price")

    # Execute manual sell
    auto_sell_service.execute_auto_sell(db, trade, symbol, current_price, "MANUAL")

    return {"message": "Trade sold successfully", "exit_price": current_price}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
