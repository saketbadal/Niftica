# utils/telegram.py
import requests
from config.config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, AUTHORIZED_USERS
from utils.logging_setup import logger

def send_telegram_message(message, chat_id=None):
    """Send message to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        
        payload = {
            "chat_id": chat_id or TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            logger.info(f"Telegram message sent successfully")
            return True
        else:
            logger.error(f"Failed to send Telegram message: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")
        return False

def setup_telegram_bot():
    """Initialize Telegram bot and send startup message"""
    startup_msg = (
        "🚀 <b>Niftica Started</b> 🚀\n\n"
        "System is now monitoring Nifty options and will provide:\n"
        "• Buy/Sell/Hold recommendations\n"
        "• Market analysis with AI insights\n"
        "• Open Interest dynamics\n"
        "• News sentiment analysis\n\n"
        "Commands:\n"
        "/status - System status\n"
        "/analysis - Latest market analysis\n"
        "/performance - Performance metrics\n"
        "/help - Show all commands"
    )
    send_telegram_message(startup_msg)

def is_authorized(chat_id):
    """Check if a chat ID is authorized"""
    return str(chat_id) in AUTHORIZED_USERS