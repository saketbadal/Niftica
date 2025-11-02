# data_enrichment/news_scraper.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from utils.logging_setup import logger
from utils.market import get_current_ist_time

class NewsScraper:
    def __init__(self):
        self.sources = {
            'moneycontrol': 'https://www.moneycontrol.com/news/business/markets/',
            'et': 'https://economictimes.indiatimes.com/markets'
        }
    
    def fetch_recent_news(self, hours=4):
        """Fetch recent market news"""
        try:
            news_items = []
            cutoff_time = get_current_ist_time() - timedelta(hours=hours)
            
            # This is a simplified version - in production, use proper news APIs
            # For demo, returning sample news items
            sample_news = [
                {
                    'title': 'Nifty hits new high on strong global cues',
                    'sentiment': 'positive',
                    'impact': 'high',
                    'time': get_current_ist_time() - timedelta(hours=1)
                },
                {
                    'title': 'FII selling continues for third day',
                    'sentiment': 'negative',
                    'impact': 'medium',
                    'time': get_current_ist_time() - timedelta(hours=2)
                }
            ]
            
            return sample_news
            
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []
    
    def analyze_sentiment(self, news_items):
        """Analyze overall news sentiment"""
        if not news_items:
            return {'sentiment': 'neutral', 'score': 0}
        
        positive = sum(1 for item in news_items if item['sentiment'] == 'positive')
        negative = sum(1 for item in news_items if item['sentiment'] == 'negative')
        
        total = len(news_items)
        score = (positive - negative) / total if total > 0 else 0
        
        if score > 0.3:
            sentiment = 'positive'
        elif score < -0.3:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': round(score, 2),
            'positive_count': positive,
            'negative_count': negative
        }