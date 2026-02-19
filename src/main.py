# Market Monitoring System
# Entry point for the application

import logging
import time
import schedule
import html
from dotenv import load_dotenv
import os

from src.database.db import db_instance
from src.services.market_data import MarketDataService
from src.services.indicators import IndicatorService
from src.services.scoring import ScoringService
from src.services.alerting import AlertService
from src.services.plotting import ChartService
from src.services.symbol_service import SymbolService
from src.services.auto_sell import AutoSellService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress yfinance 404 noise
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

def run_scan():
    logger.info("Starting Market Scan...")
    db_gen = db_instance.get_db()
    db = next(db_gen)
    
    signals_found = 0  # Track number of signals found
    
    try:
        # Initialize Services
        market_data_service = MarketDataService(db)
        indicator_service = IndicatorService(db)
        scoring_service = ScoringService()
        scoring_service = ScoringService()
        alert_service = AlertService()
        chart_service = ChartService()
        symbol_service = SymbolService(db)
        
        # Sync Nifty 500 High Cap Stocks (> 10,000 Cr)
        # Note: This is a heavy operation.
        logger.info("Initializing High Cap Stock Sync...")
        symbol_service.sync_high_cap_stocks()
        
        # Run auto-sell checks for existing trades
        auto_sell_service = AutoSellService()
        auto_sell_service.check_and_execute_auto_sells()
        
        # Get active symbols
        symbols = db.query(Symbol).filter(Symbol.is_active == True).all()
        if not symbols:
            logger.warning("No active symbols found after sync. Check market cap threshold or data source.")
            return
        
        for symbol in symbols:
            try:
                # 1. Update Data
                market_data_service.fetch_and_store(symbol.ticker)
                
                # 2. Analyze
                df = indicator_service.load_data(symbol.ticker)
                if df.empty:
                    continue
                    
                df = indicator_service.calculate_indicators(df)
                
                # 3. Score (Latest Candle)
                latest_row = df.iloc[-1]
                result = scoring_service.score_signal(latest_row, df)
                
        logger.info(f"Analysis for {symbol.ticker}: Score={result['score']} ({result['confidence']})")
                
                # 4. Save Signal - Convert numpy types to Python native types
                signal = TradeSignal(
                    symbol_id=symbol.id,
                    rsi=float(latest_row['RSI']),
                    atr=float(latest_row['ATR']),
                    score=result['score'],
                    confidence=result['confidence'],
                    direction=result['direction']
                )
                try:
                    db.add(signal)
                    db.commit()
                except Exception as db_error:
                    logger.error(f"Database error for {symbol.ticker}: {db_error}")
                    db.rollback()
                    continue
                
                # Track signals for summary
                if result['confidence'] in ["High", "Medium", "Low"]:
                    signals_found += 1
                
                # 5. Alert
                if result['confidence'] in ["High", "Medium", "Low"]:
                    # Get company info
                    company_name = symbol.name or "N/A"
                    company_type = symbol_service.get_company_type(symbol.sector or "", symbol.industry or "")
                    
                    # Construct formatted message
                    ticker = symbol.ticker
                    score = result['score']
                    conf = result['confidence']
                    price = latest_row['close']
                    direction = result['direction']
                    # Escape reasons to avoid HTML parsing errors (e.g. < 30)
                    reasons_str = "\n".join([f"• {html.escape(r)}" for r in result['reasons']])
                    
                    # Emoji Map
                    icon = "🟢" if direction == "LONG" else "🔴"
                    
                    # Format Volume (e.g. 1.5M, 500K)
                    vol = latest_row['volume']
                    if vol >= 1_000_000:
                        vol_str = f"{vol/1_000_000:.2f}M"
                    elif vol >= 1_000:
                        vol_str = f"{vol/1_000:.2f}K"
                    else:
                        vol_str = f"{vol:.0f}"

                    if direction == "LONG":
                        strategy_logic = (
                            f"<b>📈 Oversold Mean-Reversion Setup Detected</b>\n\n"
                            f"• RSI(14) deeply oversold and turning upward\n"
                            f"• Consecutive bullish Heikin Ashi candles indicate selling exhaustion\n"
                            f"• Volume expansion confirms short-term buyer participation\n"
                            f"• Price extended below key moving averages — bounce probability elevated\n"
                            f"• Counter-trend trade: quick relief rally expected, not a trend reversal"
                        )
                    else:
                         strategy_logic = (
                            f"• <b>RSI &gt; 70:</b> Price is Overbought (Expensive). Expecting a drop.\n"
                            f"• <b>Heikin Ashi:</b> Red Candle = Bearish Reversal starting.\n"
                            f"• <b>Volume:</b> High volume confirms sellers are aggressive."
                        )

                    msg = (
                        f"🚨 <b>Trade Signal Detected For {ticker} - {latest_row.name.strftime('%d-%b-%Y')}</b>\n\n"
                        f"{icon} <b>Action:</b> {'BUY' if direction == 'LONG' else 'SELL'}\n"
                        f"🧭 <b>Direction:</b> {direction}\n"
                        f"🏢 <b>Company:</b> {company_name}\n"
                        f"📊 <b>Type:</b> {company_type}\n"
                        f"💎 <b>Symbol:</b> {ticker}\n"
                        f"📊 <b>Score:</b> {score}/100 ({conf})\n"
                        f"📉 <b>RSI:</b> {latest_row['RSI']:.2f}\n"
                        f"💰 <b>Price:</b> ₹{price:.2f}\n"
                        f"🕒 <b>Time:</b> {latest_row.name.strftime('%H:%M:%S')}\n\n"
                        
                        f"🕯️ <b>Heikin Ashi Candles:</b>\n"
                        f"O: {latest_row['HA_Open']:.2f} | H: {latest_row['HA_High']:.2f}\n"
                        f"L: {latest_row['HA_Low']:.2f}  | C: {latest_row['HA_Close']:.2f}\n"
                        f"Vol: {vol_str}\n\n"

                        f"<b>Logic / Reasons:</b>\n"
                        f"{reasons_str}\n\n"
                        
                        f"💡 <b>Strategy Explanation:</b>\n"
                        f"{strategy_logic}\n\n"
                    )

                    # Fetch and add news if available
                    headline, link = market_data_service.fetch_latest_news(ticker)
                    if headline:
                        msg += (
                            f"📰 <b>News:</b> <a href='{link}'>{headline}</a>\n\n"
                            if link else f"📰 <b>News:</b> {headline}\n\n"
                        )

                    # Fetch and add Corporate Actions
                    actions = market_data_service.fetch_corporate_actions(ticker)
                    if actions:
                        msg += f"🗓️ <b>Corporate Actions:</b>\n"
                        for event, date in actions.items():
                            # Format date if it's a date object
                            d_str = date.strftime('%d-%b-%Y') if hasattr(date, 'strftime') else str(date)
                            msg += f"• {event}: {d_str}\n"
                        msg += "\n"

                    # Fetch and add Institutional & Insider Data
                    shareholding = market_data_service.fetch_shareholding_data(ticker)
                    
                    # 1. Institutional Holders (Top 10)
                    inst_holders = shareholding.get('institutional_holders')
                    if inst_holders is not None and not inst_holders.empty:
                        msg += f"🏦 <b>Top Inst. Holders:</b>\n"
                        try:
                            # Usually columns: Holder, Shares, Date Reported, % Out, Value
                            top_10 = inst_holders.head(10)
                            for index, row in top_10.iterrows():
                                name = row.get('Holder', 'N/A')
                                pct = row.get('% Out', 'N/A')
                                # format pct if it's a number
                                if isinstance(pct, (int, float)):
                                    pct_str = f"{pct*100:.2f}%" if pct < 1 else f"{pct:.2f}%" 
                                else:
                                    pct_str = str(pct)
                                msg += f"• {name} ({pct_str})\n"
                        except Exception as e:
                            logger.error(f"Error formatting inst holders: {e}")
                        msg += "\n"
                    else:
                        # Fallback to Major Holders (Ownership Breakdown)
                        major_holders = shareholding.get('major_holders')
                        if major_holders is not None and not major_holders.empty:
                            msg += f"🏦 <b>Ownership Breakdown:</b>\n"
                            try:
                                # Convert to dict for easier access if it's a DF 
                                # Structure: Breakdown (index) -> Value (col)
                                # Row indices: insidersPercentHeld, institutionsPercentHeld, etc.
                                if 'Value' in major_holders.columns:
                                    mh_dict = major_holders['Value'].to_dict()
                                    
                                    # Insiders
                                    insider_pct = mh_dict.get('insidersPercentHeld', 0)
                                    if insider_pct:
                                         msg += f"• Insiders: {float(insider_pct)*100:.2f}%\n"
                                    
                                    # Institutions
                                    inst_pct = mh_dict.get('institutionsPercentHeld', 0)
                                    inst_count = mh_dict.get('institutionsCount', 0)
                                    if inst_pct:
                                        msg += f"• Institutions: {float(inst_pct)*100:.2f}%"
                                        if inst_count:
                                            msg += f" (Count: {int(inst_count)})"
                                        msg += "\n"
                            except Exception as e:
                                logger.error(f"Error formatting major holders: {e}")
                            
                            # Add direct link for detailed breakdown since names are missing
                            clean_ticker = ticker.replace(".NS", "").replace(".BO", "")
                            msg += f"🔗 <a href='https://www.screener.in/company/{clean_ticker}/#shareholding'>View Detailed Holders</a>\n"
                            msg += "\n"

                    # 2. Mutual Fund Holders (Top 5)
                    mf_holders = shareholding.get('mutualfund_holders')
                    if mf_holders is not None and not mf_holders.empty:
                        msg += f"💰 <b>Top MF Holders:</b>\n"
                        try:
                            top_5 = mf_holders.head(5)
                            for index, row in top_5.iterrows():
                                name = row.get('Holder', 'N/A')
                                pct = row.get('% Out', 'N/A')
                                if isinstance(pct, (int, float)):
                                    pct_str = f"{pct*100:.2f}%" if pct < 1 else f"{pct:.2f}%"
                                else:
                                    pct_str = str(pct)
                                msg += f"• {name} ({pct_str})\n"
                        except Exception as e:
                            logger.error(f"Error formatting MF holders: {e}")
                        msg += "\n"

                    # 3. Insider Transactions (Last 3)
                    insider_tx = market_data_service.fetch_insider_trading(ticker)
                    if insider_tx is not None and not insider_tx.empty:
                        msg += f"🤝 <b>Recent Insider Activity:</b>\n"
                        try:
                            # Sort by Date desc just in case
                            if 'Start Date' in insider_tx.columns:
                                insider_tx = insider_tx.sort_values(by='Start Date', ascending=False)
                            
                            last_3 = insider_tx.head(3)
                            for index, row in last_3.iterrows():
                                # Columns often vary. Common: Insider, Position, Transaction, Shares, Value, Start Date
                                name = row.get('Insider', 'Unknown')
                                url_col = row.get('Text', '') # Sometimes description is in Text
                                shares = row.get('Shares', 0)
                                shares_str = f"{int(shares):,}" if isinstance(shares, (int, float)) else str(shares)
                                date_val = row.get('Start Date', '')
                                date_str = date_val.strftime('%d-%b') if hasattr(date_val, 'strftime') else str(date_val)
                                
                                msg += f"• {date_str}: {name} ({shares_str})\n"
                        except Exception as e:
                            logger.error(f"Error formatting insider tx: {e}")
                        msg += "\n"

                    msg += f"<i>Generated by Market Bahubali System</i>"
                    
                    # Generate Chart
                    chart_buf = chart_service.generate_chart(df, ticker)
                    
                    # Create Inline Keyboard (Buy Button) with deep link
                    buttons = None
                    if direction == "LONG":
                        # For channels, use deep link that opens private chat with bot
                        from src.config.settings import Config
                        bot_username = Config.TELEGRAM_BOT_USERNAME
                        deep_link_param = f"buy_{signal.id}_{ticker}_{price:.2f}"
                        deep_link = f"https://t.me/{bot_username}?start={deep_link_param}"
                        
                        buttons = [[
                            {"text": f"🚀 Buy Now (₹{price:.2f})", "url": deep_link}
                        ]]
                    
                    campaign_channel_id = None
                    if direction == "LONG":
                        campaign_channel_id = alert_service.buy_channel_id
                    elif direction == "SHORT":
                        campaign_channel_id = alert_service.sell_channel_id

                    if chart_buf:
                        logger.info(f"Sending Telegram Alert with Chart:\n{msg}")
                        alert_service.send_telegram_photo(msg, chart_buf, buttons=buttons, specific_chat_id=campaign_channel_id)
                    else:
                        logger.info(f"Chart generation failed. Sending text only:\n{msg}")
                        alert_service.send_telegram_message(msg, specific_chat_id=campaign_channel_id)

            except Exception as e:
                logger.error(f"Error analyzing {symbol.ticker}: {e}")
                continue
        
        # Send summary message if no signals found
        if signals_found == 0:
            from datetime import datetime
            current_time = datetime.now()
            
            no_signal_msg = (
                f"📊 <b>Market Scan Complete</b>\n\n"
                f"🔍 <b>Status:</b> No Trade Signals Detected\n"
                f"📅 <b>Date:</b> {current_time.strftime('%d-%b-%Y')}\n"
                f"🕒 <b>Time:</b> {current_time.strftime('%H:%M:%S')}\n\n"
                f"✅ <b>Scanned:</b> {len(symbols)} active symbols\n"
                f"📈 <b>Market Condition:</b> No high-confidence setups found\n\n"
                f"💡 <b>Note:</b> System is running normally. Will alert when opportunities arise.\n\n"
                f"<i>Generated by Tranforge Solutions LLP</i>"
            )
            
            logger.info("No signals found. Sending summary message.")
            alert_service.send_telegram_message(no_signal_msg)
        else:
            logger.info(f"Scan completed. Found {signals_found} signals.")
                
    except Exception as e:
        logger.error(f"Error during scan: {e}")
    finally:
        db.close()
        logger.info("Market Scan Completed.")

def main():
    load_dotenv()
    
    # Initialize DB (Create Tables)
    db_instance.create_tables()
    logger.info("Database initialized.")

    # Schedule - twice daily
    # schedule.every().day.at("09:30").do(run_scan)
    # schedule.every().day.at("16:00").do(run_scan)
    
    # Run immediately for verification
    api_key_check = os.getenv("TELEGRAM_BOT_TOKEN")
    if not api_key_check:
        logger.warning("TELEGRAM_BOT_TOKEN is not set. Alerts will be skipped.")

    run_scan()

    logger.info("Scheduler started. Waiting for jobs...")
    # while True:
    #    schedule.run_pending()
    #    time.sleep(1)

if __name__ == "__main__":
    main()
