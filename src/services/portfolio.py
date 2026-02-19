#!/usr/bin/env python3
"""
Portfolio service to track user performance
"""

import logging
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from src.database.db import db_instance
from src.models.models import PaperTrade, Symbol, Subscriber
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PortfolioService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_portfolio(self, chat_id: str) -> dict:
        """Get complete portfolio summary for user"""
        subscriber = self.db.query(Subscriber).filter(Subscriber.chat_id == chat_id).first()
        if not subscriber:
            return None
        
        # Open trades
        open_trades = self.db.query(PaperTrade).filter(
            PaperTrade.subscriber_id == subscriber.id,
            PaperTrade.status == "OPEN"
        ).all()
        
        # Closed trades
        closed_trades = self.db.query(PaperTrade).filter(
            PaperTrade.subscriber_id == subscriber.id,
            PaperTrade.status == "CLOSED"
        ).all()
        
        # Calculate metrics
        total_pnl = sum(trade.pnl or 0 for trade in closed_trades)
        total_trades = len(closed_trades)
        winning_trades = len([t for t in closed_trades if (t.pnl or 0) > 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        return {
            "subscriber": subscriber,
            "open_trades": open_trades,
            "closed_trades": closed_trades,
            "total_pnl": total_pnl,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": total_trades - winning_trades,
            "win_rate": win_rate,
            "avg_pnl": total_pnl / total_trades if total_trades > 0 else 0
        }
    
    def format_portfolio_message(self, portfolio: dict) -> str:
        """Format portfolio data into telegram message"""
        if not portfolio:
            return "❌ Portfolio not found. Please /start first."
        
        open_trades = portfolio["open_trades"]
        pnl_emoji = "🟢" if portfolio["total_pnl"] > 0 else "🔴"
        
        msg = (
            f"📊 <b>Your Portfolio Summary</b>\n\n"
            f"👤 <b>Trader:</b> {portfolio['subscriber'].chat_id}\n"
            f"📅 <b>Since:</b> {portfolio['subscriber'].joined_at.strftime('%d-%b-%Y')}\n\n"
            
            f"📈 <b>Performance:</b>\n"
            f"{pnl_emoji} Total P&L: ₹{portfolio['total_pnl']:.2f}\n"
            f"🎯 Win Rate: {portfolio['win_rate']:.1f}%\n"
            f"📊 Total Trades: {portfolio['total_trades']}\n"
            f"✅ Winners: {portfolio['winning_trades']}\n"
            f"❌ Losers: {portfolio['losing_trades']}\n"
            f"📊 Avg P&L: ₹{portfolio['avg_pnl']:.2f}\n\n"
        )
        
        if open_trades:
            msg += f"🔄 <b>Open Positions ({len(open_trades)}):</b>\n"
            for trade in open_trades[:5]:  # Show max 5
                symbol = self.db.query(Symbol).filter(Symbol.id == trade.symbol_id).first()
                days_held = (datetime.now() - trade.entry_time).days
                msg += (
                    f"• {symbol.ticker} @ ₹{trade.entry_price:.2f} "
                    f"({days_held}d ago)\n"
                )
            if len(open_trades) > 5:
                msg += f"... and {len(open_trades) - 5} more\n"
        else:
            msg += "💤 <b>No open positions</b>\n"
        
        msg += f"\n⚠️ <b>Paper Trading Only</b> - No real money involved"
        
        return msg
    
    def get_leaderboard(self, limit: int = 10) -> list:
        """Get top performers leaderboard"""
        # Get users with their total P&L
        results = self.db.query(
            Subscriber.chat_id,
            func.sum(PaperTrade.pnl).label('total_pnl'),
            func.count(PaperTrade.id).label('trade_count'),
            func.sum(
                case(
                    (PaperTrade.pnl > 0, 1),
                    else_=0
                )
            ).label('wins')
        ).join(
            PaperTrade, Subscriber.id == PaperTrade.subscriber_id
        ).filter(
            PaperTrade.status == "CLOSED"
        ).group_by(
            Subscriber.id, Subscriber.chat_id
        ).order_by(
            func.sum(PaperTrade.pnl).desc()
        ).limit(limit).all()
        
        return results