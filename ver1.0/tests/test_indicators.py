# tests/test_indicators.py
import pytest
import pandas as pd
import numpy as np
from utils.indicators import calculate_supertrend, calculate_adx

def test_supertrend_calculation():
    """Test SuperTrend calculation"""
    # Create sample data
    dates = pd.date_range('2024-01-01', periods=100, freq='5T')
    data = {
        'date': dates,
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 101,
        'low': np.random.randn(100).cumsum() + 99,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100)
    }
    df = pd.DataFrame(data)
    
    # Calculate SuperTrend
    result = calculate_supertrend(df, period=10, multiplier=3)
    
    assert result is not None
    assert 'supertrend' in result.columns
    assert 'trend' in result.columns
    assert len(result) == len(df)

def test_adx_calculation():
    """Test ADX calculation"""
    # Similar test structure for ADX
    pass