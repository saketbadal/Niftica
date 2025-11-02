# data_enrichment/vix_monitor.py
from utils.logging_setup import logger
from scanner.data_fetcher import DataFetcher

class VIXMonitor:
    def __init__(self):
        self.fetcher = DataFetcher()
        self.vix_symbol = "INDIA VIX"
    
    def get_current_vix(self):
        """Get current India VIX value"""
        try:
            # Note: You'll need to map this to actual VIX symbol
            vix_data = self.fetcher.get_ltp("INDIAVIX")
            return vix_data
        except Exception as e:
            logger.error(f"Error fetching VIX: {e}")
            # Return a default moderate VIX if fetch fails
            return 15.0
    
    def analyze_volatility_regime(self):
        """Analyze current volatility regime"""
        try:
            vix = self.get_current_vix()
            
            if vix < 12:
                regime = "low"
                description = "Low volatility - Favorable for trend following"
            elif vix < 20:
                regime = "normal"
                description = "Normal volatility - Standard market conditions"
            elif vix < 30:
                regime = "elevated"
                description = "Elevated volatility - Higher risk, wider stops needed"
            else:
                regime = "high"
                description = "High volatility - Extreme caution advised"
            
            return {
                'vix': vix,
                'regime': regime,
                'description': description
            }
            
        except Exception as e:
            logger.error(f"Error analyzing volatility: {e}")
            return {
                'vix': 15.0,
                'regime': 'normal',
                'description': 'Unable to fetch VIX, assuming normal conditions'
            }