# config/config.py
import os
import pytz
from dotenv import load_dotenv

load_dotenv()

# Timezone
IST = pytz.timezone('Asia/Kolkata')

# Kite Connect
KITE_API_KEY = os.environ.get("KITE_API_KEY", "")
KITE_API_SECRET = os.environ.get("KITE_API_SECRET", "")
KITE_ACCESS_TOKEN = os.environ.get("KITE_ACCESS_TOKEN", "")

# Telegram
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
AUTHORIZED_USERS = os.environ.get("AUTHORIZED_USERS", TELEGRAM_CHAT_ID).split(",")

# SuperTrend Parameters
ST_PERIOD_1 = int(os.environ.get("ST_PERIOD_1", "10"))
ST_MULTIPLIER_1 = float(os.environ.get("ST_MULTIPLIER_1", "1"))
ST_PERIOD_2 = int(os.environ.get("ST_PERIOD_2", "10"))
ST_MULTIPLIER_2 = float(os.environ.get("ST_MULTIPLIER_2", "3"))

# Market Hours (IST)
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 15
MARKET_CLOSE_HOUR = 15
MARKET_CLOSE_MINUTE = 30

# Scanner Settings
DEFAULT_SYMBOLS = os.environ.get("DEFAULT_SYMBOLS", "").split(",")
CANDLE_INTERVAL = os.environ.get("CANDLE_INTERVAL", "5minute")
UPDATE_INTERVAL_SECONDS = int(os.environ.get("UPDATE_INTERVAL_SECONDS", "300"))

# Lot Sizes
LOT_SIZES = {
    'NIFTY': 75
}

def validate_config():
    """Validate essential configuration"""
    if not KITE_API_KEY or not KITE_API_SECRET:
        return False
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    return True