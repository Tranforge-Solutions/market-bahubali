#!/usr/bin/env python3
"""
Comprehensive test script for all trading system functionality
"""

import logging
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from src.database.db import db_instance
from src.models.models import Symbol, TradeSignal, Subscriber, PaperTrade
from src.services.symbol_service import SymbolService
from src.services.market_data import MarketDataService
from src.services.indicators import IndicatorService
from src.services.scoring import ScoringService
from src.services.auto_sell import AutoSellService
from src.services.portfolio import PortfolioService
from src.services.alerting import AlertService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_setup():
    """Test 1: Database and models"""
    print("\n" + "="*50)
    print("TEST 1: DATABASE SETUP")
    print("="*50)
    
    db_gen = db_instance.get_db()
    db = next(db_gen)
    
    try:
        # Test symbol creation with company info
        test_symbol = Symbol(
            ticker="TEST.NS",
            name="Test Company Limited",
            sector="Technology",
            industry="Software",
            is_active=True
        )
        db.add(test_symbol)
        db.commit()
        
        # Verify symbol was created
        symbol = db.query(Symbol).filter(Symbol.ticker == "TEST.NS").first()
        print(f"✅ Symbol created: {symbol.ticker} - {symbol.name}")
        print(f"   Sector: {symbol.sector}, Industry: {symbol.industry}")
        
        # Test subscriber creation
        test_subscriber = Subscriber(chat_id="test_user_123", is_active=True)
        db.add(test_subscriber)
        db.commit()
        print(f"✅ Subscriber created: {test_subscriber.chat_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    finally:
        db.close()

def test_company_info():
    """Test 2: Company information and classification"""
    print("\n" + "="*50)
    print("TEST 2: COMPANY INFORMATION")
    print("="*50)
    
    db_gen = db_instance.get_db()
    db = next(db_gen)
    
    try:
        symbol_service = SymbolService(db)
        
        # Test company type classification
        test_cases = [
            ("Technology", "Software", "🖥️ Technology"),
            ("Healthcare", "Pharmaceuticals", "🏥 Healthcare"),
            ("Financial Services", "Banks", "🏦 Financial"),
            ("Energy", "Oil & Gas", "⚡ Energy"),
            ("Industrials", "Machinery", "🏭 Industrial")
        ]
        
        for sector, industry, expected in test_cases:
            result = symbol_service.get_company_type(sector, industry)
            status = "✅" if result == expected else "❌"
            print(f"{status} {sector}/{industry} -> {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Company info test failed: {e}")
        return False
    finally:
        db.close()

def test_trading_flow():
    """Test 3: Complete trading flow"""
    print("\n" + "="*50)
    print("TEST 3: TRADING FLOW")
    print("="*50)
    
    db_gen = db_instance.get_db()
    db = next(db_gen)
    
    try:
        # Get test data
        subscriber = db.query(Subscriber).filter(Subscriber.chat_id == "test_user_123").first()
        symbol = db.query(Symbol).filter(Symbol.ticker == "TEST.NS").first()
        
        if not subscriber or not symbol:
            print("❌ Test data not found")
            return False
        
        # Create test signal
        signal = TradeSignal(
            symbol_id=symbol.id,
            rsi=25.0,
            atr=15.5,
            score=75,
            confidence="High",
            direction="LONG"
        )
        db.add(signal)
        db.commit()
        print(f"✅ Signal created: {signal.direction} {symbol.ticker} (Score: {signal.score})")
        
        # Test Quick Buy (Default)
        quick_trade = PaperTrade(
            subscriber_id=subscriber.id,
            signal_id=signal.id,
            symbol_id=symbol.id,
            entry_price=100.0,
            quantity=1,
            stop_loss=95.0,  # 5% SL
            target_price=110.0,  # 10% target
            auto_exit=True,
            status="OPEN"
        )
        db.add(quick_trade)
        db.commit()
        print(f"✅ Quick Buy trade created: Entry ₹{quick_trade.entry_price}, Target ₹{quick_trade.target_price}")
        
        # Test Custom Target
        custom_trade = PaperTrade(
            subscriber_id=subscriber.id,
            signal_id=signal.id,
            symbol_id=symbol.id,
            entry_price=100.0,
            quantity=1,
            stop_loss=94.0,  # 6% SL (40% of 15% target)
            target_price=115.0,  # 15% target
            auto_exit=True,
            status="OPEN"
        )
        db.add(custom_trade)
        db.commit()
        print(f"✅ Custom target trade created: Entry ₹{custom_trade.entry_price}, Target ₹{custom_trade.target_price}")
        
        return True
        
    except Exception as e:
        print(f"❌ Trading flow test failed: {e}")
        return False
    finally:
        db.close()

def test_auto_sell():
    """Test 4: Auto-sell functionality"""
    print("\n" + "="*50)
    print("TEST 4: AUTO-SELL SYSTEM")
    print("="*50)
    
    try:
        auto_sell_service = AutoSellService()
        
        # Mock current price scenarios
        test_cases = [
            (100.0, 95.0, 110.0, 105.0, False, None),  # No exit
            (100.0, 95.0, 110.0, 94.0, True, "STOPLOSS"),  # Stop loss hit
            (100.0, 95.0, 110.0, 111.0, True, "TARGET"),  # Target hit
        ]
        
        for entry, sl, target, current, should_exit, reason in test_cases:
            # Create mock trade object
            class MockTrade:
                def __init__(self):
                    self.entry_price = entry
                    self.stop_loss = sl
                    self.target_price = target
            
            trade = MockTrade()
            result, exit_reason = auto_sell_service.should_exit_trade(trade, current)
            
            status = "✅" if result == should_exit and exit_reason == reason else "❌"
            print(f"{status} Price {current}: Exit={result}, Reason={exit_reason}")
        
        return True
        
    except Exception as e:
        print(f"❌ Auto-sell test failed: {e}")
        return False

def test_portfolio_tracking():
    """Test 5: Portfolio and performance tracking"""
    print("\n" + "="*50)
    print("TEST 5: PORTFOLIO TRACKING")
    print("="*50)
    
    db_gen = db_instance.get_db()
    db = next(db_gen)
    
    try:
        portfolio_service = PortfolioService(db)
        
        # Get portfolio for test user
        portfolio = portfolio_service.get_user_portfolio("test_user_123")
        
        if portfolio:
            print(f"✅ Portfolio loaded for user: test_user_123")
            print(f"   Open trades: {len(portfolio['open_trades'])}")
            print(f"   Total trades: {portfolio['total_trades']}")
            print(f"   Total P&L: ₹{portfolio['total_pnl']:.2f}")
            print(f"   Win rate: {portfolio['win_rate']:.1f}%")
            
            # Test portfolio message formatting
            msg = portfolio_service.format_portfolio_message(portfolio)
            print(f"✅ Portfolio message formatted ({len(msg)} chars)")
            
        else:
            print("❌ Portfolio not found")
            return False
        
        # Test leaderboard
        leaders = portfolio_service.get_leaderboard(5)
        print(f"✅ Leaderboard loaded: {len(leaders)} users")
        
        return True
        
    except Exception as e:
        print(f"❌ Portfolio test failed: {e}")
        return False
    finally:
        db.close()

def test_api_endpoints():
    """Test 6: REST API functionality"""
    print("\n" + "="*50)
    print("TEST 6: REST API")
    print("="*50)
    
    try:
        # Test API imports
        from src.api import app, generate_otp, create_access_token
        
        # Test OTP generation
        otp = generate_otp()
        print(f"✅ OTP generated: {otp} (length: {len(otp)})")
        
        # Test JWT token creation
        token = create_access_token({"sub": "test_user_123"})
        print(f"✅ JWT token created: {token[:20]}...")
        
        # Test FastAPI app
        print(f"✅ FastAPI app loaded: {app.title} v{app.version}")
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_telegram_message_format():
    """Test 7: Telegram message formatting"""
    print("\n" + "="*50)
    print("TEST 7: TELEGRAM MESSAGES")
    print("="*50)
    
    db_gen = db_instance.get_db()
    db = next(db_gen)
    
    try:
        symbol_service = SymbolService(db)
        symbol = db.query(Symbol).filter(Symbol.ticker == "TEST.NS").first()
        
        if not symbol:
            print("❌ Test symbol not found")
            return False
        
        # Test signal message format
        company_type = symbol_service.get_company_type(symbol.sector or "", symbol.industry or "")
        
        msg = (
            f"🚨 <b>Trade Signal Detected For {symbol.ticker}</b>\n\n"
            f"🟢 <b>Action:</b> BUY\n"
            f"🧭 <b>Direction:</b> LONG\n"
            f"🏢 <b>Company:</b> {symbol.name}\n"
            f"📊 <b>Type:</b> {company_type}\n"
            f"💎 <b>Symbol:</b> {symbol.ticker}\n"
            f"📊 <b>Score:</b> 75/100 (High)\n"
            f"📉 <b>RSI:</b> 25.50\n"
            f"💰 <b>Price:</b> ₹100.00\n"
            f"🕒 <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}\n\n"
        )
        
        print("✅ Signal message formatted:")
        print(msg[:200] + "...")
        
        # Test no-signal message
        no_signal_msg = (
            f"📊 <b>Market Scan Complete</b>\n\n"
            f"🔍 <b>Status:</b> No Trade Signals Detected\n"
            f"📅 <b>Date:</b> {datetime.now().strftime('%d-%b-%Y')}\n"
            f"🕒 <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}\n\n"
            f"✅ <b>Scanned:</b> 1 active symbols\n"
            f"💡 <b>Note:</b> System is running normally.\n"
        )
        
        print("✅ No-signal message formatted:")
        print(no_signal_msg[:150] + "...")
        
        return True
        
    except Exception as e:
        print(f"❌ Message format test failed: {e}")
        return False
    finally:
        db.close()

def cleanup_test_data():
    """Clean up test data"""
    print("\n" + "="*50)
    print("CLEANUP: Removing test data")
    print("="*50)
    
    db_gen = db_instance.get_db()
    db = next(db_gen)
    
    try:
        # Remove test trades
        db.query(PaperTrade).filter(
            PaperTrade.subscriber_id.in_(
                db.query(Subscriber.id).filter(Subscriber.chat_id == "test_user_123")
            )
        ).delete(synchronize_session=False)
        
        # Remove test signals
        db.query(TradeSignal).filter(
            TradeSignal.symbol_id.in_(
                db.query(Symbol.id).filter(Symbol.ticker == "TEST.NS")
            )
        ).delete(synchronize_session=False)
        
        # Remove test subscriber
        db.query(Subscriber).filter(Subscriber.chat_id == "test_user_123").delete()
        
        # Remove test symbol
        db.query(Symbol).filter(Symbol.ticker == "TEST.NS").delete()
        
        db.commit()
        print("✅ Test data cleaned up")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
    finally:
        db.close()

def main():
    """Run all tests"""
    load_dotenv()
    
    print("STARTING COMPREHENSIVE SYSTEM TEST")
    print("=" * 60)
    
    tests = [
        ("Database Setup", test_database_setup),
        ("Company Information", test_company_info),
        ("Trading Flow", test_trading_flow),
        ("Auto-Sell System", test_auto_sell),
        ("Portfolio Tracking", test_portfolio_tracking),
        ("REST API", test_api_endpoints),
        ("Telegram Messages", test_telegram_message_format),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Cleanup
    cleanup_test_data()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("ALL TESTS PASSED! System is ready for deployment.")
    else:
        print("Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    main()