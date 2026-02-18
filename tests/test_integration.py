import sys
from unittest.mock import MagicMock

# Mock yfinance before it is imported by the application code
sys.modules["yfinance"] = MagicMock()

import pytest
import pandas as pd
from datetime import datetime
from src.services.market_data import MarketDataService
from src.services.indicators import IndicatorService
from src.services.scoring import ScoringService
from src.models.models import Symbol, OHLCV, TradeSignal
from unittest.mock import patch

def test_full_flow_integration(db_session):
    """
    Tests the data flow from Data Storage -> Analysis -> Scoring -> Signal Logic.
    Does NOT make actual network calls (mocks yfinance).
    """
    
    # 1. Setup Data (Mocking yfinance to avoid network dependency in tests)
    mock_data = pd.DataFrame({
        'Open': [100.0, 101.0, 102.0] * 20, # Generate enough rows for indicators
        'High': [105.0, 106.0, 107.0] * 20,
        'Low': [95.0, 96.0, 97.0] * 20,
        'Close': [102.0, 103.0, 104.0] * 20,
        'Volume': [1000, 1500, 2000] * 20
    })
    # Create timestamps index
    mock_data.index = pd.date_range(start="2023-01-01", periods=60, freq="D")
    
    with patch('yfinance.download', return_value=mock_data):
        market_service = MarketDataService(db_session)
        market_service.fetch_and_store("TEST-TICKER")
    
    # Verify Data Stored
    symbol = db_session.query(Symbol).filter(Symbol.ticker == "TEST-TICKER").first()
    assert symbol is not None
    ohlcv_count = db_session.query(OHLCV).filter(OHLCV.symbol_id == symbol.id).count()
    assert ohlcv_count == 60
    
    # 2. Test Indicators
    indicator_service = IndicatorService(db_session)
    df = indicator_service.load_data("TEST-TICKER")
    df = indicator_service.calculate_indicators(df)
    
    assert 'RSI' in df.columns
    assert 'HA_Close' in df.columns
    assert 'HA_Green' in df.columns
    
    # Check simple calculation (SMA) isn't NaN for the last value
    assert not pd.isna(df.iloc[-1]['SMA_20'])
    
    # 3. Test Scoring
    scoring_service = ScoringService()
    latest_row = df.iloc[-1]
    score_result = scoring_service.score_signal(latest_row)
    
    assert "score" in score_result
    assert "confidence" in score_result
    assert "direction" in score_result
    
    # 4. Save Signal (Mimic Main Loop)
    signal = TradeSignal(
        symbol_id=symbol.id,
        rsi=latest_row['RSI'],
        atr=latest_row['ATR'],
        score=score_result['score'],
        confidence=score_result['confidence'],
        direction=score_result['direction']
    )
    db_session.add(signal)
    db_session.commit()
    
    saved_signal = db_session.query(TradeSignal).filter(TradeSignal.symbol_id == symbol.id).first()
    assert saved_signal is not None
    assert saved_signal.score == score_result['score']
    assert saved_signal.direction == score_result['direction']
