#!/usr/bin/env python3
"""
Test script to demonstrate company information functionality
"""

import logging
from dotenv import load_dotenv
from src.database.db import db_instance
from src.models.models import Symbol
from src.services.symbol_service import SymbolService
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_company_info():
    """Test the company information functionality"""
    load_dotenv()
    
    db_gen = db_instance.get_db()
    db = next(db_gen)
    
    try:
        symbol_service = SymbolService(db)
        
        # Test with TIMKEN.NS
        ticker = "TIMKEN.NS"
        
        # Check if symbol exists
        symbol = db.query(Symbol).filter(Symbol.ticker == ticker).first()
        
        if not symbol:
            logger.info(f"Symbol {ticker} not found. Creating...")
            # Create symbol with company info
            import yfinance as yf
            t = yf.Ticker(ticker)
            info = t.info
            
            symbol = Symbol(
                ticker=ticker,
                name=info.get('longName') or info.get('shortName', ''),
                sector=info.get('sector', ''),
                industry=info.get('industry', ''),
                is_active=True
            )
            db.add(symbol)
            db.commit()
        
        # Display symbol information
        company_type = symbol_service.get_company_type(symbol.sector or "", symbol.industry or "")
        
        symbol_data = {
            "id": symbol.id,
            "ticker": symbol.ticker,
            "name": symbol.name,
            "sector": symbol.sector,
            "industry": symbol.industry,
            "company_type": company_type,
            "is_active": symbol.is_active
        }
        
        print("\n" + "="*50)
        print("COMPANY INFORMATION TEST")
        print("="*50)
        print(f"Original issue: {{'id':273,'ticker':'TIMKEN.NS','name':null,'is_active':true}}")
        print(f"Fixed result:")
        print(json.dumps(symbol_data, indent=2))
        print("\n" + "="*50)
        print("TELEGRAM MESSAGE PREVIEW")
        print("="*50)
        
        # Simulate telegram message format
        telegram_msg = f"""🚨 Trade Signal Detected For {symbol.ticker}

🟢 Action: BUY
🧭 Direction: LONG
🏢 Company: {symbol.name or 'N/A'}
📊 Type: {company_type}
💎 Symbol: {symbol.ticker}
📊 Score: 75/100 (High)
📉 RSI: 28.50
💰 Price: ₹2,450.75
🕒 Time: 15:30:00

🕯️ Heikin Ashi Candles:
O: 2445.20 | H: 2455.80
L: 2440.10  | C: 2450.75
Vol: 1.2M

Logic / Reasons:
• Oversold & Rising RSI (RSI: 28.5, Rising for 3 candles)
• Bullish Momentum Confirmed (2 Green HA Candles, Close Rising)
• High Volume Conviction (>1.2x 20-day avg)

💡 Strategy Explanation:
📈 Oversold Mean-Reversion Setup Detected

• RSI(14) deeply oversold and turning upward
• Consecutive bullish Heikin Ashi candles indicate selling exhaustion
• Volume expansion confirms short-term buyer participation
• Price extended below key moving averages — bounce probability elevated
• Counter-trend trade: quick relief rally expected, not a trend reversal"""
        
        print(telegram_msg)
        print("\n" + "="*50)
        
    except Exception as e:
        logger.error(f"Error during test: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_company_info()