#!/usr/bin/env python3
"""
Script to update existing symbols with missing name, sector, and industry information
"""

import logging
from dotenv import load_dotenv
from src.database.db import db_instance
from src.models.models import Symbol
from src.services.symbol_service import SymbolService
import yfinance as yf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_missing_symbol_info():
    """Update symbols that have missing name, sector, or industry information"""
    load_dotenv()
    
    db_gen = db_instance.get_db()
    db = next(db_gen)
    
    try:
        symbol_service = SymbolService(db)
        
        # Get symbols with missing information
        symbols = db.query(Symbol).filter(
            (Symbol.name.is_(None)) | 
            (Symbol.name == '') |
            (Symbol.sector.is_(None)) | 
            (Symbol.sector == '') |
            (Symbol.industry.is_(None)) | 
            (Symbol.industry == '')
        ).all()
        
        logger.info(f"Found {len(symbols)} symbols with missing information")
        
        updated_count = 0
        for symbol in symbols:
            try:
                logger.info(f"Updating info for {symbol.ticker}...")
                
                # Fetch company info from yfinance
                ticker_obj = yf.Ticker(symbol.ticker)
                info = ticker_obj.info
                
                # Update fields if they're missing
                if not symbol.name:
                    symbol.name = info.get('longName') or info.get('shortName', '')
                
                if not symbol.sector:
                    symbol.sector = info.get('sector', '')
                
                if not symbol.industry:
                    symbol.industry = info.get('industry', '')
                
                db.commit()
                updated_count += 1
                
                company_type = symbol_service.get_company_type(symbol.sector or "", symbol.industry or "")
                logger.info(f"✅ Updated {symbol.ticker}: {symbol.name} ({company_type})")
                
            except Exception as e:
                logger.error(f"Error updating {symbol.ticker}: {e}")
                db.rollback()
                continue
        
        logger.info(f"Successfully updated {updated_count} symbols")
        
    except Exception as e:
        logger.error(f"Error during update: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    update_missing_symbol_info()