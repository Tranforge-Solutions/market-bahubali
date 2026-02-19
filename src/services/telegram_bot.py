import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from sqlalchemy.orm import Session
from src.database.db import db_instance
from src.models.models import Subscriber, PaperTrade, TradeSignal, Symbol
from src.config.settings import Config
from datetime import datetime

logger = logging.getLogger(__name__)

class TelegramBotHandler:
    def __init__(self):
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command - subscribe user and handle deep links"""
        chat_id = str(update.effective_chat.id)
        db = db_instance.SessionLocal()
        
        try:
            # Check if this is a deep link with signal data
            if context.args and len(context.args) > 0:
                # Parse deep link: buy_SIGNAL_ID_TICKER_PRICE
                deep_link_data = context.args[0]
                if deep_link_data.startswith("buy_"):
                    parts = deep_link_data.replace("buy_", "").split("_")
                    if len(parts) >= 3:
                        signal_id = int(parts[0])
                        ticker = parts[1]
                        price = float(parts[2])
                        
                        # Show buy options directly
                        subscriber = db.query(Subscriber).filter(Subscriber.chat_id == chat_id).first()
                        if not subscriber:
                            subscriber = Subscriber(chat_id=chat_id, is_active=True)
                            db.add(subscriber)
                            db.commit()
                        
                        # Check if already has open trade
                        symbol = db.query(Symbol).filter(Symbol.ticker == ticker).first()
                        if symbol:
                            existing_trade = db.query(PaperTrade).filter(
                                PaperTrade.subscriber_id == subscriber.id,
                                PaperTrade.symbol_id == symbol.id,
                                PaperTrade.status == "OPEN"
                            ).first()
                            
                            if existing_trade:
                                await update.message.reply_text(f"⚠️ You already have an open trade for {ticker}.")
                                return
                        
                        # Show order options
                        keyboard = [
                            [InlineKeyboardButton("📊 Quick Buy (Default)", callback_data=f"QUICK_BUY:{signal_id}:{ticker}:{price}")],
                            [InlineKeyboardButton("⚙️ Configure Order", callback_data=f"CONFIG:{signal_id}:{ticker}:{price}")],
                            [InlineKeyboardButton("❌ Cancel", callback_data="CANCEL")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        
                        await update.message.reply_text(
                            f"🎯 {ticker} @ ₹{price:.2f}\n\n"
                            f"Choose order type:",
                            reply_markup=reply_markup
                        )
                        return
            
            # Regular /start without deep link
            subscriber = db.query(Subscriber).filter(Subscriber.chat_id == chat_id).first()
            if not subscriber:
                subscriber = Subscriber(chat_id=chat_id, is_active=True)
                db.add(subscriber)
                db.commit()
                await update.message.reply_text(
                    "✅ Welcome to Market Monitor Paper Trading!\n\n"
                    "⚠️ DISCLAIMER: This is a simulated trading environment for testing and educational purposes. "
                    "No real trades are executed.\n\n"
                    "You will receive trading signals in the channel. Click BUY button to place paper trades in this private chat."
                )
            else:
                subscriber.is_active = True
                db.commit()
                await update.message.reply_text("Welcome back! You're subscribed to trading signals.")
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            await update.message.reply_text("Error subscribing. Please try again.")
        finally:
            db.close()
    
    async def handle_buy_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle BUY button click"""
        query = update.callback_query
        await query.answer()
        
        # Parse callback data: BUY:TICKER:PRICE:SIGNAL_ID
        data = query.data.split(":")
        if len(data) < 4:
            await query.edit_message_text("Invalid signal data.")
            return
        
        action, ticker, price, signal_id = data[0], data[1], float(data[2]), int(data[3])
        chat_id = str(query.from_user.id)
        
        db = db_instance.SessionLocal()
        try:
            # Get subscriber
            subscriber = db.query(Subscriber).filter(Subscriber.chat_id == chat_id).first()
            if not subscriber:
                await query.edit_message_text("Please /start first to subscribe.")
                return
            
            # Check if already has open trade for this symbol
            symbol = db.query(Symbol).filter(Symbol.ticker == ticker).first()
            if not symbol:
                await query.edit_message_text("Symbol not found.")
                return
            
            existing_trade = db.query(PaperTrade).filter(
                PaperTrade.subscriber_id == subscriber.id,
                PaperTrade.symbol_id == symbol.id,
                PaperTrade.status == "OPEN"
            ).first()
            
            if existing_trade:
                await query.edit_message_text(f"⚠️ You already have an open trade for {ticker}.")
                return
            
            # Show order configuration options
            keyboard = [
                [InlineKeyboardButton("📊 Quick Buy (Default)", callback_data=f"QUICK_BUY:{signal_id}:{ticker}:{price}")],
                [InlineKeyboardButton("⚙️ Configure Order", callback_data=f"CONFIG:{signal_id}:{ticker}:{price}")],
                [InlineKeyboardButton("❌ Cancel", callback_data="CANCEL")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"🎯 {ticker} @ ₹{price:.2f}\n\n"
                f"Choose order type:",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error handling buy: {e}")
            await query.edit_message_text("Error processing order.")
        finally:
            db.close()
    
    async def handle_quick_buy(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle quick buy with default parameters"""
        query = update.callback_query
        await query.answer()
        
        # Parse: QUICK_BUY:SIGNAL_ID:TICKER:PRICE
        data = query.data.split(":")
        signal_id, ticker, price = int(data[1]), data[2], float(data[3])
        chat_id = str(query.from_user.id)
        
        db = db_instance.SessionLocal()
        try:
            subscriber = db.query(Subscriber).filter(Subscriber.chat_id == chat_id).first()
            symbol = db.query(Symbol).filter(Symbol.ticker == ticker).first()
            signal = db.query(TradeSignal).filter(TradeSignal.id == signal_id).first()
            
            if not all([subscriber, symbol, signal]):
                await query.edit_message_text("Error: Invalid data.")
                return
            
            # Default parameters
            quantity = 1
            stop_loss = price * 0.95  # 5% SL
            target = price * 1.10  # 10% target
            
            # Create paper trade
            trade = PaperTrade(
                subscriber_id=subscriber.id,
                signal_id=signal_id,
                symbol_id=symbol.id,
                entry_price=price,
                quantity=quantity,
                stop_loss=stop_loss,
                target_price=target,
                auto_exit=True,
                status="OPEN"
            )
            db.add(trade)
            db.commit()
            
            # Show SELL button
            keyboard = [[InlineKeyboardButton("🔴 SELL", callback_data=f"SELL:{trade.id}:{ticker}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"✅ Paper Trade Opened\n\n"
                f"📊 {ticker}\n"
                f"💰 Entry: ₹{price:.2f}\n"
                f"📉 Stop Loss: ₹{stop_loss:.2f} (-5%)\n"
                f"📈 Target: ₹{target:.2f} (+10%)\n"
                f"🔢 Qty: {quantity}\n"
                f"🤖 Auto-exit: Enabled\n\n"
                f"⚠️ This is a simulated trade.",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in quick buy: {e}")
            await query.edit_message_text("Error creating trade.")
        finally:
            db.close()
    
    async def handle_sell_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle SELL button click"""
        query = update.callback_query
        await query.answer()
        
        # Parse: SELL:TRADE_ID:TICKER
        data = query.data.split(":")
        trade_id, ticker = int(data[1]), data[2]
        chat_id = str(query.from_user.id)
        
        db = db_instance.SessionLocal()
        try:
            subscriber = db.query(Subscriber).filter(Subscriber.chat_id == chat_id).first()
            trade = db.query(PaperTrade).filter(
                PaperTrade.id == trade_id,
                PaperTrade.subscriber_id == subscriber.id,
                PaperTrade.status == "OPEN"
            ).first()
            
            if not trade:
                await query.edit_message_text("Trade not found or already closed.")
                return
            
            # Get current price (simplified - use last close)
            symbol = db.query(Symbol).filter(Symbol.id == trade.symbol_id).first()
            from src.services.market_data import MarketDataService
            market_service = MarketDataService(db)
            current_price = trade.entry_price * 1.05  # Placeholder - should fetch real price
            
            # Close trade
            trade.exit_price = current_price
            trade.exit_time = datetime.now()
            trade.exit_reason = "MANUAL"
            trade.status = "CLOSED"
            trade.pnl = (current_price - trade.entry_price) * trade.quantity
            trade.pnl_percent = ((current_price - trade.entry_price) / trade.entry_price) * 100
            db.commit()
            
            pnl_emoji = "🟢" if trade.pnl > 0 else "🔴"
            
            await query.edit_message_text(
                f"✅ Trade Closed\n\n"
                f"📊 {ticker}\n"
                f"💰 Entry: ₹{trade.entry_price:.2f}\n"
                f"💰 Exit: ₹{current_price:.2f}\n"
                f"{pnl_emoji} P&L: ₹{trade.pnl:.2f} ({trade.pnl_percent:+.2f}%)\n"
                f"🔢 Qty: {trade.quantity}\n\n"
                f"⚠️ This was a simulated trade."
            )
            
        except Exception as e:
            logger.error(f"Error in sell: {e}")
            await query.edit_message_text("Error closing trade.")
        finally:
            db.close()
    
    def setup_handlers(self, application: Application):
        """Setup all command and callback handlers"""
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("mytrades", self.my_trades_command))
        application.add_handler(CallbackQueryHandler(self.handle_buy_callback, pattern="^BUY:"))
        application.add_handler(CallbackQueryHandler(self.handle_quick_buy, pattern="^QUICK_BUY:"))
        application.add_handler(CallbackQueryHandler(self.handle_sell_callback, pattern="^SELL:"))
    
    async def my_trades_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's open trades"""
        chat_id = str(update.effective_chat.id)
        db = db_instance.SessionLocal()
        
        try:
            subscriber = db.query(Subscriber).filter(Subscriber.chat_id == chat_id).first()
            if not subscriber:
                await update.message.reply_text("Please /start first to subscribe.")
                return
            
            open_trades = db.query(PaperTrade).filter(
                PaperTrade.subscriber_id == subscriber.id,
                PaperTrade.status == "OPEN"
            ).all()
            
            if not open_trades:
                await update.message.reply_text("📊 No open trades.")
                return
            
            msg = "📊 Your Open Trades:\n\n"
            for trade in open_trades:
                symbol = db.query(Symbol).filter(Symbol.id == trade.symbol_id).first()
                msg += (
                    f"📊 {symbol.ticker}\n"
                    f"💰 Entry: ₹{trade.entry_price:.2f}\n"
                    f"📉 SL: ₹{trade.stop_loss:.2f}\n"
                    f"📈 Target: ₹{trade.target_price:.2f}\n"
                    f"🔢 Qty: {trade.quantity}\n\n"
                )
                
                # Add SELL button for each trade
                keyboard = [[InlineKeyboardButton("🔴 SELL", callback_data=f"SELL:{trade.id}:{symbol.ticker}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(msg, reply_markup=reply_markup if open_trades else None)
            
        except Exception as e:
            logger.error(f"Error in mytrades: {e}")
            await update.message.reply_text("Error fetching trades.")
        finally:
            db.close()
    
    def run(self):
        """Run the bot"""
        application = Application.builder().token(self.bot_token).build()
        self.setup_handlers(application)
        application.run_polling()
