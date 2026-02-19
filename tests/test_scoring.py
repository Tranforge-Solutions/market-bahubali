import pytest
import pandas as pd
from src.services.scoring import ScoringService
from src.config.settings import Config

@pytest.fixture
def scoring_service():
    return ScoringService()

def test_scoring_long_setup(scoring_service):
    """Test LONG setup with RSI rising trend."""
    # Create test dataframe with RSI rising pattern
    data = {
        'RSI': [20, 22, 25, 28],  # Rising RSI
        'close': [95, 97, 100, 102],
        'SMA_200': [90, 90, 90, 90],  # Uptrend
        'HA_Green': [False, False, True, True],  # Recent green candles
        'HA_Close': [95, 97, 100, 102],  # Rising closes
        'Vol_Z': [1.0, 1.5, 2.0, 2.5],
        'volume': [1000, 1200, 1500, 1800]
    }
    df = pd.DataFrame(data)
    df.index = pd.date_range('2024-01-01', periods=4, freq='D')
    
    # Test latest row
    latest_row = df.iloc[-1]
    result = scoring_service.score_signal(latest_row, df)
    
    # Should detect LONG signal due to oversold + rising RSI
    assert result['direction'] == "LONG"
    assert result['score'] >= scoring_service.CONFIDENCE_LOW
    assert len(result['reasons']) > 0

def test_scoring_short_setup(scoring_service):
    """Test SHORT setup with RSI falling trend."""
    # Create test dataframe with RSI falling pattern
    data = {
        'RSI': [78, 76, 74, 72],  # Falling RSI from overbought
        'close': [105, 103, 100, 98],
        'SMA_200': [110, 110, 110, 110],  # Downtrend
        'HA_Green': [True, True, False, False],  # Recent red candles
        'HA_Close': [105, 103, 100, 98],  # Falling closes
        'Vol_Z': [1.0, 1.5, 2.0, 2.5],
        'volume': [1000, 1200, 1500, 1800]
    }
    df = pd.DataFrame(data)
    df.index = pd.date_range('2024-01-01', periods=4, freq='D')
    
    # Test latest row
    latest_row = df.iloc[-1]
    result = scoring_service.score_signal(latest_row, df)
    
    # Should detect SHORT signal due to overbought + falling RSI
    assert result['direction'] == "SHORT"
    assert result['score'] >= scoring_service.CONFIDENCE_LOW
    assert len(result['reasons']) > 0

def test_scoring_neutral(scoring_service):
    """Test Neutral state."""
    row = pd.Series({
        'RSI': 50,
        'close': 100,
        'HA_Green': True,
        'Vol_Z': 0,
        'volume': 1000
    })
    result = scoring_service.score_signal(row)
    assert result['direction'] == "NEUTRAL"
    assert result['score'] == 0
