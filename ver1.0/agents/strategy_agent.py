# agents/strategy_agent.py
import json
from google.cloud import aiplatform
from utils.logging_setup import logger
from config.config_ai import GCP_PROJECT_ID, VERTEX_LOCATION, VERTEX_MODEL, AGENT_TEMPERATURE

class StrategyAgent:
    def __init__(self):
        # Initialize Vertex AI
        aiplatform.init(project=GCP_PROJECT_ID, location=VERTEX_LOCATION)
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize Vertex AI model"""
        try:
            from vertexai.generative_models import GenerativeModel
            self.model = GenerativeModel(VERTEX_MODEL)
            logger.info("Vertex AI model initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Vertex AI model: {e}")
    
    def generate_recommendation(self, market_data, technical_data, sentiment_data):
        """Generate trading recommendation using AI"""
        try:
            # Construct prompt
            prompt = self._build_prompt(market_data, technical_data, sentiment_data)
            
            # Generate response
            if self.model:
                response = self.model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": AGENT_TEMPERATURE,
                        "max_output_tokens": 2048,
                    }
                )
                
                # Parse response
                return self._parse_ai_response(response.text)
            else:
                # Fallback to rule-based system
                return self._rule_based_recommendation(market_data, technical_data)
                
        except Exception as e:
            logger.error(f"Error generating AI recommendation: {e}")
            return self._rule_based_recommendation(market_data, technical_data)
    
    def _build_prompt(self, market, technical, sentiment):
        """Build prompt for AI model"""
        prompt = f"""
You are an expert options trader analyzing NIFTY options. Based on the following data, provide a trading recommendation.

TECHNICAL INDICATORS:
- Current Price: {technical.get('ltp', 'N/A')}
- SuperTrend (10,1): {technical.get('st_10_1', {}).get('value', 'N/A')} ({technical.get('st_10_1', {}).get('trend', 'N/A')})
- SuperTrend (10,3): {technical.get('st_10_3', {}).get('value', 'N/A')} ({technical.get('st_10_3', {}).get('trend', 'N/A')})
- ADX: {technical.get('adx', 'N/A')}

MARKET ANALYSIS:
- PCR (OI): {market.get('oi_analysis', {}).get('pcr_oi', 'N/A')}
- Max CE OI Strike: {market.get('oi_analysis', {}).get('max_ce_oi_strike', 'N/A')}
- Max PE OI Strike: {market.get('oi_analysis', {}).get('max_pe_oi_strike', 'N/A')}
- VIX: {market.get('volatility', {}).get('vix', 'N/A')} ({market.get('volatility', {}).get('regime', 'N/A')})
- Market Breadth: {market.get('market_breadth', {}).get('breadth_signal', 'N/A')}
- FII Net: {market.get('institutional_activity', {}).get('fii_net', 'N/A')} Cr

SENTIMENT:
- Overall: {sentiment.get('overall_sentiment', {}).get('sentiment', 'N/A')}
- Score: {sentiment.get('overall_sentiment', {}).get('score', 'N/A')}

Based on this analysis, provide a JSON response with:
{{
    "recommendation": "BUY/SELL/HOLD",
    "confidence": 0.0-1.0,
    "strike_suggestion": "specific strike price or ATM+1, ATM-1, etc",
    "option_type": "CE/PE",
    "reasoning": "detailed explanation",
    "risk_level": "low/medium/high",
    "target_levels": ["level1", "level2"],
    "stop_loss": "price level"
}}

Focus on high-probability setups where technical indicators align with market structure and sentiment.
"""
        return prompt
    
    def _parse_ai_response(self, response_text):
        """Parse AI response to extract recommendation"""
        try:
            # Try to extract JSON from response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                recommendation = json.loads(json_str)
                
                # Validate required fields
                required = ['recommendation', 'confidence', 'reasoning']
                if all(field in recommendation for field in required):
                    return recommendation
            
            # If parsing fails, return a default
            return {
                'recommendation': 'HOLD',
                'confidence': 0.5,
                'reasoning': 'Unable to parse AI response properly',
                'parse_error': True
            }
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return {
                'recommendation': 'HOLD',
                'confidence': 0.5,
                'reasoning': f'Error parsing response: {str(e)}',
                'parse_error': True
            }
    
    def _rule_based_recommendation(self, market, technical):
        """Fallback rule-based recommendation system"""
        recommendation = 'HOLD'
        confidence = 0.5
        reasoning = []
        
        # Check SuperTrend alignment
        st1_bullish = technical.get('st_10_1', {}).get('trend') == 'bullish'
        st3_bullish = technical.get('st_10_3', {}).get('trend') == 'bullish'
        
        if st1_bullish and st3_bullish:
            recommendation = 'BUY'
            confidence = 0.7
            reasoning.append("Both SuperTrend indicators are bullish")
            
            # Check ADX for trend strength
            adx = technical.get('adx', 0)
            if adx > 25:
                confidence += 0.1
                reasoning.append(f"Strong trend with ADX at {adx}")
            elif adx < 20:
                confidence -= 0.2
                reasoning.append(f"Weak trend with ADX at {adx}")
        
        elif not st1_bullish and not st3_bullish:
            recommendation = 'SELL'
            confidence = 0.7
            reasoning.append("Both SuperTrend indicators are bearish")
        
        # Check market conditions
        if market and 'volatility' in market:
            vix = market['volatility'].get('vix', 15)
            if vix > 25:
                confidence -= 0.2
                reasoning.append(f"High volatility (VIX: {vix}) suggests caution")
        
        return {
            'recommendation': recommendation,
            'confidence': max(0.3, min(confidence, 0.9)),
            'reasoning': ' | '.join(reasoning),
            'source': 'rule_based'
        }