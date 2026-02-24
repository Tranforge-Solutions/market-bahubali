"""
Migration script to add market_cap_cr column to symbols table
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment")
    exit(1)

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        # Add market_cap_cr column
        conn.execute(text("ALTER TABLE symbols ADD COLUMN IF NOT EXISTS market_cap_cr FLOAT"))
        conn.commit()
        print("Successfully added market_cap_cr column to symbols table")
except Exception as e:
    print(f"Error: {e}")
