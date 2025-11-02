# scanner/data_fetcher.py
from datetime import timedelta
import pandas as pd
from kiteconnect import KiteConnect
from utils.logging_setup import logger
from utils.market import get_current_ist_time
from config.config import KITE_API_KEY, KITE_API_SECRET, KITE_ACCESS_TOKEN

class DataFetcher:
    def __init__(self):
        self.kite = KiteConnect(api_key=KITE_API_KEY)
        if KITE_ACCESS_TOKEN:
            self.kite.set_access_token(KITE_ACCESS_TOKEN)
        else:
            logger.error("No Kite access token available")
            
    def get_instrument_token(self, symbol, exchange="NFO"):
        """Get instrument token for a symbol"""
        try:
            instruments = self.kite.instruments(exchange)
            for inst in instruments:
                if inst['tradingsymbol'] == symbol:
                    return inst['instrument_token']
            return None
        except Exception as e:
            logger.error(f"Error getting instrument token for {symbol}: {e}")
            return None
    
    def fetch_candles(self, symbol, interval="5minute", days=5):
        """Fetch historical candles"""
        try:
            token = self.get_instrument_token(symbol)
            if not token:
                logger.error(f"No instrument token found for {symbol}")
                return None
                
            to_date = get_current_ist_time()
            from_date = to_date - timedelta(days=days)
            
            data = self.kite.historical_data(
                instrument_token=token,
                from_date=from_date,
                to_date=to_date,
                interval=interval
            )
            
            if data:
                df = pd.DataFrame(data)
                return df
            return None
            
        except Exception as e:
            logger.error(f"Error fetching candles for {symbol}: {e}")
            return None
    
    def get_ltp(self, symbol):
        """Get last traded price"""
        try:
            exchange = "NFO"
            quote = self.kite.quote(f"{exchange}:{symbol}")
            return quote[f"{exchange}:{symbol}"]['last_price']
        except Exception as e:
            logger.error(f"Error getting LTP for {symbol}: {e}")
            return None
    
    def get_quote(self, symbol):
        """Get full quote data"""
        try:
            exchange = "NFO"
            return self.kite.quote(f"{exchange}:{symbol}")
        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {e}")
            return None