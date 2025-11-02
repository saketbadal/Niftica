# utils/logging_setup.py
import logging
import os
from datetime import datetime
import pytz

IST = pytz.timezone('Asia/Kolkata')

class ISTFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, IST)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.strftime("%Y-%m-%d %H:%M:%S IST")

def setup_logging():
    os.makedirs('logs', exist_ok=True)
    
    logger = logging.getLogger("niftica")
    logger.setLevel(logging.INFO)
    
    formatter = ISTFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler('logs/recommender.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logging()