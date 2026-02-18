import pytest
import pandas as pd
from src.services.scoring import ScoringService

@pytest.fixture
def scoring_service():
    return ScoringService()

def test_scoring_long_setup(scoring_service):
    """Test LONG setup (Oversold RSI + Green HA)."""
    row = pd.Series({
        'RSI': 25,
        'close': 100,
        'SMA_200': 90, # Uptrend
        'HA_Green': True, # Confirmation
        'Vol_Z': 2.5
    })
    result = scoring_service.score_signal(row)
    assert result['direction'] == "LONG"
    assert result['score'] >= 70 # High Confidence (40+20+15+10 = 85)
    assert "Oversold RSI" in result['reasons'][0]
    assert "Heikin Ashi" in str(result['reasons'])

def test_scoring_short_setup(scoring_service):
    """Test SHORT setup (Overbought RSI + Red HA)."""
    row = pd.Series({
        'RSI': 75,
        'close': 100,
        'SMA_200': 110, # Downtrend
        'HA_Green': False, # Red Candle confirmation
        'Vol_Z': 2.5
    })
    result = scoring_service.score_signal(row)
    assert result['direction'] == "SHORT"
    assert result['score'] >= 70 # High Confidence
    assert "Overbought RSI" in result['reasons'][0]
    assert "Heikin Ashi" in str(result['reasons'])

def test_scoring_neutral(scoring_service):
    """Test Neutral state."""
    row = pd.Series({
        'RSI': 50,
        'close': 100,
        'HA_Green': True,
        'Vol_Z': 0
    })
    result = scoring_service.score_signal(row)
    assert result['direction'] == "NEUTRAL"
    assert result['score'] == 0
