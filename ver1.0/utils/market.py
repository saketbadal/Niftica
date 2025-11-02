# utils/market.py
from datetime import datetime, timedelta
import time
from config.config import IST, MARKET_OPEN_HOUR, MARKET_OPEN_MINUTE, MARKET_CLOSE_HOUR, MARKET_CLOSE_MINUTE
from utils.logging_setup import logger

def get_current_ist_time():
    """Get current time in IST timezone"""
    return datetime.now(IST)

def is_market_open():
    """Check if the market is currently open"""
    now = get_current_ist_time()
    
    if now.weekday() >= 5:  # Saturday or Sunday
        return False
    
    market_start = now.replace(hour=MARKET_OPEN_HOUR, minute=MARKET_OPEN_MINUTE, second=0, microsecond=0)
    market_end = now.replace(hour=MARKET_CLOSE_HOUR, minute=MARKET_CLOSE_MINUTE, second=0, microsecond=0)
    
    return market_start <= now <= market_end

def wait_for_next_interval():
    """Wait until the next 5-minute interval"""
    now = get_current_ist_time()
    current_minute = now.minute
    
    next_5min = current_minute - (current_minute % 5) + 5
    if next_5min >= 60:
        next_hour = now.hour + 1
        next_5min = 0
    else:
        next_hour = now.hour
    
    next_time = now.replace(hour=next_hour, minute=next_5min, second=5, microsecond=0)
    wait_seconds = (next_time - now).total_seconds()
    
    if wait_seconds > 0:
        logger.info(f"Waiting {wait_seconds:.0f}s for next interval: {next_time.strftime('%H:%M:%S')} IST")
        time.sleep(wait_seconds)
    
    return next_time