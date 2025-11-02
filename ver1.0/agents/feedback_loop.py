# agents/feedback_loop.py
from google.cloud import firestore
from datetime import datetime, timedelta
from utils.logging_setup import logger
from utils.market import get_current_ist_time

class FeedbackLoop:
    def __init__(self):
        self.db = firestore.Client()
        self.collection = 'recommendation_feedback'
    
    def store_recommendation(self, symbol, recommendation_data):
        """Store recommendation for future analysis"""
        try:
            doc_data = {
                'symbol': symbol,
                'timestamp': get_current_ist_time(),
                'recommendation': recommendation_data['recommendation'],
                'confidence': recommendation_data['confidence'],
                'reasoning': recommendation_data['reasoning'],
                'market_data': recommendation_data.get('market_snapshot', {}),
                'verified': False,
                'actual_outcome': None
            }
            
            doc_ref = self.db.collection(self.collection).add(doc_data)
            logger.info(f"Stored recommendation: {doc_ref[1].id}")
            return doc_ref[1].id
            
        except Exception as e:
            logger.error(f"Error storing recommendation: {e}")
            return None
    
    def verify_recommendation(self, recommendation_id, actual_movement, pnl=None):
        """Verify a past recommendation with actual outcome"""
        try:
            doc_ref = self.db.collection(self.collection).document(recommendation_id)
            doc_ref.update({
                'verified': True,
                'actual_outcome': actual_movement,
                'pnl': pnl,
                'verification_time': get_current_ist_time()
            })
            
            logger.info(f"Verified recommendation {recommendation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying recommendation: {e}")
            return False
    
    def get_performance_metrics(self, days=30):
        """Calculate performance metrics from past recommendations"""
        try:
            cutoff_date = get_current_ist_time() - timedelta(days=days)
            
            # Query verified recommendations
            query = self.db.collection(self.collection).where(
                'timestamp', '>=', cutoff_date
            ).where('verified', '==', True)
            
            docs = query.get()
            
            metrics = {
                'total_recommendations': 0,
                'correct_predictions': 0,
                'accuracy': 0,
                'avg_confidence': 0,
                'by_recommendation': {
                    'BUY': {'total': 0, 'correct': 0},
                    'SELL': {'total': 0, 'correct': 0},
                    'HOLD': {'total': 0, 'correct': 0}
                }
            }
            
            total_confidence = 0
            
            for doc in docs:
                data = doc.to_dict()
                recommendation = data['recommendation']
                actual = data['actual_outcome']
                confidence = data['confidence']
                
                metrics['total_recommendations'] += 1
                total_confidence += confidence
                
                # Update recommendation-specific metrics
                metrics['by_recommendation'][recommendation]['total'] += 1
                
                # Check if prediction was correct
                if self._is_prediction_correct(recommendation, actual):
                    metrics['correct_predictions'] += 1
                    metrics['by_recommendation'][recommendation]['correct'] += 1
            
            # Calculate aggregates
            if metrics['total_recommendations'] > 0:
                metrics['accuracy'] = metrics['correct_predictions'] / metrics['total_recommendations']
                metrics['avg_confidence'] = total_confidence / metrics['total_recommendations']
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return None
    
    def _is_prediction_correct(self, recommendation, actual_outcome):
        """Check if prediction was correct"""
        if recommendation == 'BUY' and actual_outcome in ['bullish', 'up']:
            return True
        elif recommendation == 'SELL' and actual_outcome in ['bearish', 'down']:
            return True
        elif recommendation == 'HOLD' and actual_outcome in ['neutral', 'sideways']:
            return True
        return False
    
    def get_learning_insights(self):
        """Extract insights for improving the system"""
        try:
            metrics = self.get_performance_metrics(days=7)
            
            if not metrics or metrics['total_recommendations'] < 20:
                return None
            
            insights = []
            
            # Overall accuracy insight
            accuracy = metrics['accuracy']
            if accuracy < 0.5:
                insights.append("System accuracy below 50% - review strategy parameters")
            elif accuracy > 0.7:
                insights.append("System performing well with >70% accuracy")
            
            # Recommendation-specific insights
            for rec_type, data in metrics['by_recommendation'].items():
                if data['total'] > 5:
                    rec_accuracy = data['correct'] / data['total']
                    if rec_accuracy < 0.4:
                        insights.append(f"{rec_type} signals underperforming - accuracy: {rec_accuracy:.1%}")
            
            # Confidence calibration
            avg_confidence = metrics['avg_confidence']
            if abs(avg_confidence - accuracy) > 0.2:
                if avg_confidence > accuracy:
                    insights.append("System overconfident - reduce confidence scores")
                else:
                    insights.append("System underconfident - increase confidence for accurate predictions")
            
            return {
                'insights': insights,
                'metrics': metrics,
                'recommendation_adjustments': self._suggest_adjustments(metrics)
            }
            
        except Exception as e:
            logger.error(f"Error getting learning insights: {e}")
            return None
    
    def _suggest_adjustments(self, metrics):
        """Suggest parameter adjustments based on performance"""
        adjustments = []
        
        if metrics['accuracy'] < 0.5:
            adjustments.append({
                'parameter': 'ADX_THRESHOLD',
                'current': 20,
                'suggested': 25,
                'reason': 'Increase to filter weak trends'
            })
        
        # Check by recommendation type
        for rec_type, data in metrics['by_recommendation'].items():
            if data['total'] > 5 and data['correct'] / data['total'] < 0.4:
                if rec_type == 'BUY':
                    adjustments.append({
                        'parameter': 'SUPERTREND_MULTIPLIER',
                        'current': 3,
                        'suggested': 3.5,
                        'reason': f'Reduce false {rec_type} signals'
                    })
        
        return adjustments