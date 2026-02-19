#!/usr/bin/env python3
"""
Auto-sell service to handle automatic trade exits
"""

import logging
from datetime import datetime
from sqlalchemy.orm import Session
from src.database.db import db_instance
from src.models.models import PaperTrade, Symbol
from src.services.market_data import MarketDataService
from src.services.alerting import AlertService
import yfinance as yf

logger = logging.getLogger(__name__)

class AutoSellService:
    def __init__(self):
        self.alert_service = AlertService()
    
    def check_and_execute_auto_sells(self):
        """Check all open trades for auto-sell conditions"""
        db_gen = db_instance.get_db()
        db = next(db_gen)
        
        try:
            # Get all open trades with auto-exit enabled
            open_trades = db.query(PaperTrade).filter(
                PaperTrade.status == "OPEN",
                PaperTrade.auto_exit == True
            ).all()
            
            logger.info(f"Checking {len(open_trades)} open trades for auto-sell")
            
            for trade in open_trades:
                try:
                    symbol = db.query(Symbol).filter(Symbol.id == trade.symbol_id).first()
                    if not symbol:
                        continue
                    
                    # Get current price
                    current_price = self.get_current_price(symbol.ticker)
                    if not current_price:
                        continue
                    
                    # Check exit conditions
                    should_exit, exit_reason = self.should_exit_trade(trade, current_price)
                    
                    if should_exit:
                        self.execute_auto_sell(db, trade, symbol, current_price, exit_reason)
                        
                except Exception as e:
                    logger.error(f"Error checking trade {trade.id}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error in auto-sell check: {e}")
        finally:
            db.close()
    
    def get_current_price(self, ticker: str) -> float:
        """Get current market price for ticker"""
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="1d", interval="1m")
            if not data.empty:
                return float(data['Close'].iloc[-1])
        except Exception as e:
            logger.error(f"Error fetching price for {ticker}: {e}")
        return None
    
    def should_exit_trade(self, trade: PaperTrade, current_price: float) -> tuple:
        """Check if trade should be auto-exited"""
        # Stop Loss hit
        if trade.stop_loss and current_price <= trade.stop_loss:
            return True, "STOPLOSS"
        
        # Target hit
        if trade.target_price and current_price >= trade.target_price:
            return True, "TARGET"
        
        return False, None
    
    def execute_auto_sell(self, db: Session, trade: PaperTrade, symbol: Symbol, exit_price: float, exit_reason: str):
        """Execute automatic sell"""
        try:
            # Update trade
            trade.exit_price = exit_price
            trade.exit_time = datetime.now()
            trade.exit_reason = exit_reason
            trade.status = "CLOSED"
            trade.pnl = (exit_price - trade.entry_price) * trade.quantity
            trade.pnl_percent = ((exit_price - trade.entry_price) / trade.entry_price) * 100
            
            db.commit()
            
            # Send notification to user
            self.send_auto_sell_notification(trade, symbol, exit_reason)
            
            logger.info(f"Auto-sold {symbol.ticker} for user {trade.subscriber.chat_id}: {exit_reason}")
            
        except Exception as e:
            logger.error(f"Error executing auto-sell: {e}")
            db.rollback()
    
    def send_auto_sell_notification(self, trade: PaperTrade, symbol: Symbol, exit_reason: str):
        """Send auto-sell notification to user"""
        pnl_emoji = "🟢" if trade.pnl > 0 else "🔴"
        reason_emoji = "🎯" if exit_reason == "TARGET" else "🛑"
        
        msg = (
            f"{reason_emoji} <b>Auto-Sell Executed</b>\n\n"
            f"📊 {symbol.ticker}\n"
            f"🏢 {symbol.name or 'N/A'}\n"
            f"💰 Entry: ₹{trade.entry_price:.2f}\n"
            f"💰 Exit: ₹{trade.exit_price:.2f}\n"
            f"{pnl_emoji} P&L: ₹{trade.pnl:.2f} ({trade.pnl_percent:+.2f}%)\n"
            f"📝 Reason: {exit_reason}\n"
            f"🕒 Time: {trade.exit_time.strftime('%H:%M:%S')}\n\n"
            f"⚠️ This was an automated paper trade exit."
        )
        
        self.alert_service.send_telegram_message(msg, specific_chat_id=trade.subscriber.chat_id)

if __name__ == "__main__":
    service = AutoSellService()
    service.check_and_execute_auto_sells()