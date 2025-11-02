# scanner/signal_processor.py
from datetime import datetime, timedelta
from utils.logging_setup import logger
from utils.indicators import calculate_supertrend, calculate_adx
from models.recommendation import Recommendation
from agents.market_analyst import MarketAnalyst
from agents.sentiment_analyzer import SentimentAnalyzer
from agents.strategy_agent import StrategyAgent
from agents.feedback_loop import FeedbackLoop
from utils.telegram import send_telegram_message
from config.config import ST_PERIOD_1, ST_MULTIPLIER_1, ST_PERIOD_2, ST_MULTIPLIER_2

class SignalProcessor:
    def __init__(self):
        self.market_analyst = MarketAnalyst()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.strategy_agent = StrategyAgent()
        self.feedback_loop = FeedbackLoop()
        self.last_signals = {}  # Track last signal time for cooldown
    
    def process_symbol(self, symbol, df, ltp):
        """Process a symbol for potential signals"""
        try:
            # Calculate technical indicators
            technical_data = self._calculate_technicals(df, ltp)
            
            if not technical_data:
                return None
            
            # Check for signal
            if not self._check_signal_conditions(symbol, technical_data):
                return None
            
            # Get market analysis
            expiry_date = self._get_current_expiry()
            market_analysis = self.market_analyst.analyze_market_conditions(ltp, expiry_date)
            
            # Get sentiment analysis
            sentiment_analysis = self.sentiment_analyzer.analyze_market_sentiment()
            
            # Generate AI recommendation
            ai_recommendation = self.strategy_agent.generate_recommendation(
                market_analysis,
                technical_data,
                sentiment_analysis
            )
            
            # Create recommendation object
            recommendation = Recommendation(
                symbol=symbol,
                timestamp=datetime.now(),
                recommendation=ai_recommendation['recommendation'],
                confidence=ai_recommendation['confidence'],
                option_type=ai_recommendation.get('option_type'),
                strike_suggestion=ai_recommendation.get('strike_suggestion'),
                reasoning=ai_recommendation['reasoning'],
                risk_level=ai_recommendation.get('risk_level', 'medium'),
                target_levels=ai_recommendation.get('target_levels'),
                stop_loss=ai_recommendation.get('stop_loss'),
                market_snapshot={
                    'ltp': ltp,
                    'technical': technical_data,
                    'market': market_analysis,
                    'sentiment': sentiment_analysis
                }
            )
            
            # Store for feedback loop
            rec_id = self.feedback_loop.store_recommendation(symbol, recommendation.to_dict())
            
            # Send to Telegram
            self._send_recommendation(recommendation)
            
            # Update last signal time
            self.last_signals[symbol] = datetime.now()
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error processing symbol {symbol}: {e}")
            return None
    
    def _calculate_technicals(self, df, ltp):
        """Calculate technical indicators"""
        try:
            # Calculate SuperTrend
            df_st1 = calculate_supertrend(df.copy(), ST_PERIOD_1, ST_MULTIPLIER_1)
            df_st3 = calculate_supertrend(df.copy(), ST_PERIOD_2, ST_MULTIPLIER_2)
            
            if df_st1 is None or df_st3 is None:
                return None
            
            # Calculate ADX
            adx = calculate_adx(df)
            
            # Extract values
            st_10_1 = {
                'value': round(df_st1['supertrend'].iloc[-1], 2),
                'trend': df_st1['trend'].iloc[-1]
            }
            
            st_10_3 = {
                'value': round(df_st3['supertrend'].iloc[-1], 2),
                'trend': df_st3['trend'].iloc[-1]
            }
            
            return {
                'ltp': ltp,
                'st_10_1': st_10_1,
                'st_10_3': st_10_3,
                'adx': round(adx, 2) if adx else None,
                'both_bullish': st_10_1['trend'] == 'bullish' and st_10_3['trend'] == 'bullish',
                'both_bearish': st_10_1['trend'] == 'bearish' and st_10_3['trend'] == 'bearish'
            }
            
        except Exception as e:
            logger.error(f"Error calculating technicals: {e}")
            return None
    
    def _check_signal_conditions(self, symbol, technical_data):
        """Check if signal conditions are met"""
        # Check cooldown
        if symbol in self.last_signals:
            time_since_last = (datetime.now() - self.last_signals[symbol]).total_seconds()
            if time_since_last < 1800:  # 30 minutes cooldown
                return False
        
        # Check for trend alignment
        if technical_data['both_bullish'] or technical_data['both_bearish']:
            # Check ADX for trend strength
            if technical_data.get('adx', 0) > 20:
                return True
        
        return False
    
    def _get_current_expiry(self):
        """Get current weekly expiry date string"""
        # This is simplified - implement proper expiry calculation
        today = datetime.now()
        days_until_thursday = (3 - today.weekday()) % 7
        if days_until_thursday == 0 and today.hour >= 15:
            days_until_thursday = 7
        
        expiry = today + timedelta(days=days_until_thursday)
        return expiry.strftime("%y%b%d").upper()
        #The above calculation is not fully accurate for all cases. It would be better to store the future expiry dates in a config or database.
    
    def _send_recommendation(self, recommendation):
        """Send recommendation to Telegram"""
        message = recommendation.to_telegram_message()
        send_telegram_message(message)
        
        # Also send a summary for quick reading
        summary = f"📢 Quick Summary: {recommendation.recommendation} {recommendation.symbol} " \
                  f"@ {recommendation.market_snapshot['ltp']} " \
                  f"(Confidence: {recommendation.confidence:.0%})"
        send_telegram_message(summary)