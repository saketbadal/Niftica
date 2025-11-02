# scanner/scanner_loop.py
import time
import threading
from datetime import datetime
from utils.logging_setup import logger
from utils.market import is_market_open, wait_for_next_interval, get_current_ist_time
from utils.telegram import send_telegram_message
from scanner.data_fetcher import DataFetcher
from scanner.signal_processor import SignalProcessor
from config.config import DEFAULT_SYMBOLS, UPDATE_INTERVAL_SECONDS
from agents.feedback_loop import FeedbackLoop

class ScannerLoop:
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.signal_processor = SignalProcessor()
        self.feedback_loop = FeedbackLoop()
        self.active_symbols = set(DEFAULT_SYMBOLS)
        self.running = False
    
    def start(self):
        """Start the scanner loop"""
        self.running = True
        
        # Send startup message
        self._send_startup_message()
        
        while self.running:
            try:
                # Check market hours
                if not is_market_open():
                    self._handle_market_closed()
                    continue
                
                # Process each symbol
                for symbol in self.active_symbols:
                    self._process_symbol(symbol)
                
                # Send periodic updates
                self._send_periodic_update()
                
                # Wait for next interval
                wait_for_next_interval()
                
            except Exception as e:
                logger.error(f"Error in scanner loop: {e}")
                send_telegram_message(f"⚠️ Scanner Error: {str(e)}")
                time.sleep(60)  # Wait before retrying
    
    def stop(self):
        """Stop the scanner loop"""
        self.running = False
    
    def _process_symbol(self, symbol):
        """Process a single symbol"""
        try:
            # Fetch candles
            df = self.data_fetcher.fetch_candles(symbol)
            if df is None or len(df) < 100:
                logger.warning(f"Insufficient data for {symbol}")
                return
            
            # Get LTP
            ltp = self.data_fetcher.get_ltp(symbol)
            if ltp is None:
                logger.warning(f"Could not get LTP for {symbol}")
                return
            
            # Process for signals
            recommendation = self.signal_processor.process_symbol(symbol, df, ltp)
            
            if recommendation:
                logger.info(f"Signal generated for {symbol}: {recommendation.recommendation}")
            
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
    
    def _send_startup_message(self):
        """Send startup notification"""
        message = (
            "🚀 <b>Scanner Started</b> 🚀\n\n"
            f"Monitoring symbols: {', '.join(self.active_symbols)}\n"
            f"Time: {get_current_ist_time().strftime('%d-%b-%Y %H:%M:%S')} IST\n\n"
            "System will analyze:\n"
            "• SuperTrend indicators\n"
            "• Open Interest dynamics\n"
            "• Market sentiment\n"
            "• AI-powered insights"
        )
        send_telegram_message(message)
    
    def _handle_market_closed(self):
        """Handle market closed hours"""
        if hasattr(self, '_market_was_open'):
            if self._market_was_open:
                # Market just closed
                self._send_eod_summary()
                self._market_was_open = False
        
        # Sleep until next check
        time.sleep(300)  # Check every 5 minutes
    
    def _send_periodic_update(self):
        """Send periodic status updates"""
        current_time = datetime.now()
        
        # Send update every hour
        if current_time.minute < 5 and not hasattr(self, '_last_update_hour'):
            self._last_update_hour = current_time.hour
            
            # Get performance metrics
            metrics = self.feedback_loop.get_performance_metrics(days=7)
            
            if metrics:
                message = (
                    "📊 <b>Hourly Update</b> 📊\n\n"
                    f"Time: {current_time.strftime('%H:%M')} IST\n"
                    f"Active Symbols: {len(self.active_symbols)}\n\n"
                    f"<b>7-Day Performance:</b>\n"
                    f"Total Recommendations: {metrics['total_recommendations']}\n"
                    f"Accuracy: {metrics['accuracy']:.1%}\n"
                    f"Avg Confidence: {metrics['avg_confidence']:.1%}"
                )
                send_telegram_message(message)
        
        elif current_time.hour != getattr(self, '_last_update_hour', -1):
            self._last_update_hour = current_time.hour
    
    def _send_eod_summary(self):
        """Send end of day summary"""
        try:
            # Get today's recommendations
            insights = self.feedback_loop.get_learning_insights()
            
            message = (
                "📈 <b>End of Day Summary</b> 📉\n\n"
                f"Date: {datetime.now().strftime('%d-%b-%Y')}\n\n"
            )
            
            if insights and insights['metrics']:
                metrics = insights['metrics']
                message += (
                    f"<b>Today's Performance:</b>\n"
                    f"Recommendations: {metrics['total_recommendations']}\n"
                    f"Accuracy: {metrics['accuracy']:.1%}\n\n"
                )
                
                # Add insights
                if insights['insights']:
                    message += "<b>Key Insights:</b>\n"
                    for insight in insights['insights']:
                        message += f"• {insight}\n"
            else:
                message += "No recommendations generated today.\n"
            
            message += "\n🌙 Good night! See you tomorrow at 9:15 AM."
            
            send_telegram_message(message)
            
        except Exception as e:
            logger.error(f"Error sending EOD summary: {e}")

def start_scanner_thread():
    """Start scanner in a separate thread"""
    scanner = ScannerLoop()
    thread = threading.Thread(target=scanner.start)
    thread.daemon = True
    thread.start()
    return thread