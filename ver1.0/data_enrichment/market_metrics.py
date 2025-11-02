# data_enrichment/market_metrics.py

#The FII, DII activity and Advance Decline data is hardcoded as of now. It needs to be fetched from the relevant data sources in future.

import numpy as np
from utils.logging_setup import logger
from scanner.data_fetcher import DataFetcher

class MarketMetrics:
    def __init__(self):
        self.fetcher = DataFetcher()
    
    def calculate_market_breadth(self):
        """Calculate market breadth indicators"""
        try:
            # This is a simplified version - in production, you'd fetch actual advance/decline data
            # For now, we'll use a proxy based on major stocks
            
            advancing = 15  # Placeholder
            declining = 10  # Placeholder
            
            advance_decline_ratio = advancing / declining if declining > 0 else 2.0
            
            return {
                'advancing': advancing,
                'declining': declining,
                'ad_ratio': round(advance_decline_ratio, 2),
                'breadth_signal': self._interpret_breadth(advance_decline_ratio)
            }
            
        except Exception as e:
            logger.error(f"Error calculating market breadth: {e}")
            return None
    
    def _interpret_breadth(self, ad_ratio):
        """Interpret market breadth"""
        if ad_ratio > 2.0:
            return "strongly_bullish"
        elif ad_ratio > 1.2:
            return "bullish"
        elif ad_ratio < 0.5:
            return "strongly_bearish"
        elif ad_ratio < 0.8:
            return "bearish"
        else:
            return "neutral"
    
    def get_fii_dii_data(self):
        """Get FII/DII activity data"""
        try:
            # Placeholder - integrate with actual data source
            return {
                'fii_net': 1000,  # In crores
                'dii_net': -500,
                'fii_trend': 'buying',
                'dii_trend': 'selling'
            }
        except Exception as e:
            logger.error(f"Error fetching FII/DII data: {e}")
            return None