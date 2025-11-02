# agents/sentiment_analyzer.py
from utils.logging_setup import logger
from data_enrichment.news_scraper import NewsScraper

class SentimentAnalyzer:
    def __init__(self):
        self.news_scraper = NewsScraper()
    
    def analyze_market_sentiment(self):
        """Analyze overall market sentiment from news"""
        try:
            # Fetch recent news
            news_items = self.news_scraper.fetch_recent_news(hours=4)
            
            # Analyze sentiment
            sentiment_analysis = self.news_scraper.analyze_sentiment(news_items)
            
            # Add key headlines
            key_headlines = []
            for item in news_items[:3]:  # Top 3 news items
                key_headlines.append({
                    'title': item['title'],
                    'sentiment': item['sentiment'],
                    'impact': item['impact']
                })
            
            return {
                'overall_sentiment': sentiment_analysis,
                'key_headlines': key_headlines,
                'recommendation': self._sentiment_recommendation(sentiment_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {
                'overall_sentiment': {'sentiment': 'neutral', 'score': 0},
                'key_headlines': [],
                'recommendation': 'neutral'
            }
    
    def _sentiment_recommendation(self, sentiment):
        """Convert sentiment to trading recommendation"""
        score = sentiment.get('score', 0)
        
        if score > 0.5:
            return 'very_positive'
        elif score > 0.2:
            return 'positive'
        elif score < -0.5:
            return 'very_negative'
        elif score < -0.2:
            return 'negative'
        else:
            return 'neutral'