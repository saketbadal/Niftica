# app.py
import os
import threading
from flask import Flask
from dotenv import load_dotenv
from utils.logging_setup import logger
from utils.telegram import send_telegram_message, setup_telegram_bot
from scanner.scanner_loop import start_scanner_thread
from web import create_flask_app
from config.config import validate_config

# Load environment variables
load_dotenv()

# Initialize logger
logger.info("=== Nifty Options AI Recommender initializing ===")

# Validate configuration
if not validate_config():
    logger.critical("Configuration validation failed. Exiting.")
    exit(1)

# Set up Telegram bot
setup_telegram_bot()

# Start the scanner in a separate thread
scanner_thread = start_scanner_thread()

# Create Flask application
app = create_flask_app()

def main():
    """Main entry point"""
    try:
        port = int(os.environ.get("PORT", 8080))
        logger.info(f"Starting Flask app on port {port}")
        app.run(host="0.0.0.0", port=port)
    except Exception as e:
        error_msg = f"Error running Flask app: {e}"
        logger.error(error_msg, exc_info=True)
        send_telegram_message(f"❌ <b>Application Error</b> ❌\n\n{error_msg}")
        raise

if __name__ == "__main__":
    main()