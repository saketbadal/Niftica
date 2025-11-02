# web/routes.py
from flask import jsonify
from utils.market import get_current_ist_time, is_market_open
from utils.logging_setup import logger

def register_routes(app):
    """Register HTTP routes"""
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': get_current_ist_time().isoformat(),
            'market_open': is_market_open()
        })
    
    @app.route('/status', methods=['GET'])
    def status():
        """Get system status"""
        try:
            from agents.feedback_loop import FeedbackLoop
            feedback = FeedbackLoop()
            metrics = feedback.get_performance_metrics(days=1)
            
            return jsonify({
                'status': 'operational',
                'timestamp': get_current_ist_time().isoformat(),
                'market_open': is_market_open(),
                'today_recommendations': metrics.get('total_recommendations', 0) if metrics else 0,
                'accuracy': metrics.get('accuracy', 0) if metrics else 0
            })
        except Exception as e:
            logger.error(f"Error in status endpoint: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/metrics', methods=['GET'])
    def metrics():
        """Get performance metrics"""
        try:
            from agents.feedback_loop import FeedbackLoop
            feedback = FeedbackLoop()
            
            return jsonify({
                'daily': feedback.get_performance_metrics(days=1),
                'weekly': feedback.get_performance_metrics(days=7),
                'monthly': feedback.get_performance_metrics(days=30)
            })
        except Exception as e:
            logger.error(f"Error in metrics endpoint: {e}")
            return jsonify({'error': str(e)}), 500