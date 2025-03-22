import pandas as pd
import numpy as np
from app.analysis.service import FinancialAnalyzer

def test_financial_ratios():
    """Test financial ratio calculations."""
    data = {
        'revenue': [1000, 1200, 1100],
        'net income': [100, 150, 125],
        'total assets': [2000, 2100, 2050],
        'equity': [1500, 1600, 1550]
    }
    df = pd.DataFrame(data)
    analyzer = FinancialAnalyzer(df)
    
    ratios = analyzer.calculate_financial_ratios()
    
    assert 'profit_margin' in ratios
    assert abs(ratios['profit_margin'] - 0.115) < 0.01  # ~11.5%
    assert 'roa' in ratios
    assert abs(ratios['roa'] - 0.061) < 0.01  # ~6.1%

def test_trend_analysis():
    """Test trend identification."""
    data = {
        'revenue': [1000, 1100, 1200],
        'expenses': [500, 600, 550]
    }
    df = pd.DataFrame(data)
    analyzer = FinancialAnalyzer(df)
    
    trends = analyzer.find_trends()
    
    assert 'revenue' in trends
    assert trends['revenue']['trend'] == 'increasing'
    assert abs(trends['revenue']['growth_rate'] - 20.0) < 0.01  # 20% growth

def test_forecasting():
    """Test simple forecasting."""
    data = {
        'revenue': [1000, 1100, 1200, 1300, 1400]
    }
    df = pd.DataFrame(data)
    analyzer = FinancialAnalyzer(df)
    
    forecast = analyzer.forecasting_simple('revenue', periods=2)
    
    assert len(forecast) == 2
    assert all(forecast['forecast'] > 1400)  # Forecasted values should continue trend
