# web/webhook.py
from flask import request, Response
from utils.logging_setup import logger
from utils.telegram import is_authorized, send_telegram_message

def register_webhook(app):
    """Register webhook handlers"""
    
    @app.route('/telegram-webhook', methods=['POST'])
    def telegram_webhook():
        """Handle Telegram webhook"""
        try:
            data = request.get_json()
            
            if 'message' in data:
                message = data['message']
                chat_id = message.get('chat', {}).get('id')
                text = message.get('text', '')
                
                if not is_authorized(chat_id):
                    send_telegram_message("⛔ Unauthorized access", chat_id)
                    return Response(status=200)
                
                # Process commands
                response = process_command(text, chat_id)
                if response:
                    send_telegram_message(response, chat_id)
            
            return Response(status=200)
            
        except Exception as e:
            logger.error(f"Error in telegram webhook: {e}")
            return Response(status=500)

def process_command(text, chat_id):
    """Process Telegram commands"""
    if not text.startswith('/'):
        return None
    
    command = text.split()[0].lower()
    
    if command == '/status':
        from agents.feedback_loop import FeedbackLoop
        feedback = FeedbackLoop()
        metrics = feedback.get_performance_metrics(days=1)
        
        if metrics:
            return (
                f"📊 <b>System Status</b>\n\n"
                f"Today's Recommendations: {metrics['total_recommendations']}\n"
                f"Accuracy: {metrics['accuracy']:.1%}\n"
                f"Market: {'OPEN' if is_market_open() else 'CLOSED'}"
            )
        else:
            return "System is operational. No data available yet."
    
    elif command == '/performance':
        from agents.feedback_loop import FeedbackLoop
        feedback = FeedbackLoop()
        insights = feedback.get_learning_insights()
        
        if insights and insights['metrics']:
            metrics = insights['metrics']
            return (
                f"📈 <b>7-Day Performance</b>\n\n"
                f"Total Signals: {metrics['total_recommendations']}\n"
                f"Accuracy: {metrics['accuracy']:.1%}\n"
                f"Avg Confidence: {metrics['avg_confidence']:.1%}\n\n"
                f"<b>By Type:</b>\n"
                f"BUY: {metrics['by_recommendation']['BUY']['correct']}/{metrics['by_recommendation']['BUY']['total']}\n"
                f"SELL: {metrics['by_recommendation']['SELL']['correct']}/{metrics['by_recommendation']['SELL']['total']}\n"
                f"HOLD: {metrics['by_recommendation']['HOLD']['correct']}/{metrics['by_recommendation']['HOLD']['total']}"
            )
        else:
            return "Insufficient data for performance analysis."
    
    elif command == '/help':
        return (
            "🤖 <b>Available Commands</b>\n\n"
            "/status - Current system status\n"
            "/performance - Performance metrics\n"
            "/analysis - Latest market analysis\n"
            "/help - Show this help message"
        )
    
    elif command == '/analysis':
        # Trigger immediate analysis
        return "Analysis request received. Please wait..."
    
    return "Unknown command. Use /help to see available commands."