#!/usr/bin/env python3
"""
Database migration to add sector and industry columns to symbols table
"""

import logging
from dotenv import load_dotenv
from src.database.db import db_instance
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """Add sector and industry columns to symbols table"""
    load_dotenv()
    
    db_gen = db_instance.get_db()
    db = next(db_gen)
    
    try:
        # Check if columns exist
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'symbols' AND column_name IN ('sector', 'industry')
        """))
        existing_columns = [row[0] for row in result.fetchall()]
        
        # Add missing columns
        if 'sector' not in existing_columns:
            db.execute(text("ALTER TABLE symbols ADD COLUMN sector VARCHAR"))
            logger.info("Added sector column")
        
        if 'industry' not in existing_columns:
            db.execute(text("ALTER TABLE symbols ADD COLUMN industry VARCHAR"))
            logger.info("Added industry column")
        
        db.commit()
        logger.info("Database migration completed successfully")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_database()