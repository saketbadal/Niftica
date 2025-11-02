# agents/market_analyst.py
from utils.logging_setup import logger
from data_enrichment.oi_analyzer import OIAnalyzer
from data_enrichment.vix_monitor import VIXMonitor
from data_enrichment.market_metrics import MarketMetrics

class MarketAnalyst:
    def __init__(self):
        self.oi_analyzer = OIAnalyzer()
        self.vix_monitor = VIXMonitor()
        self.market_metrics = MarketMetrics()
    
    def analyze_market_conditions(self, spot_price, expiry_date):
        """Comprehensive market analysis"""
        try:
            # Gather all data
            oi_analysis = self.oi_analyzer.fetch_option_chain(spot_price, expiry_date)
            volatility = self.vix_monitor.analyze_volatility_regime()
            breadth = self.market_metrics.calculate_market_breadth()
            fii_dii = self.market_metrics.get_fii_dii_data()
            
            # Synthesize analysis
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'spot_price': spot_price,
                'oi_analysis': oi_analysis,
                'volatility': volatility,
                'market_breadth': breadth,
                'institutional_activity': fii_dii,
                'overall_bias': self._determine_overall_bias(oi_analysis, breadth, fii_dii),
                'risk_level': self._assess_risk_level(volatility, oi_analysis)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in market analysis: {e}")
            return None
    
    def _determine_overall_bias(self, oi, breadth, fii_dii):
        """Determine overall market bias"""
        scores = []
        
        # OI bias
        if oi and 'interpretation' in oi:
            oi_bias = oi['interpretation']['bias']
            if oi_bias == 'bullish':
                scores.append(1)
            elif oi_bias == 'bearish':
                scores.append(-1)
            else:
                scores.append(0)
        
        # Breadth bias
        if breadth:
            signal = breadth['breadth_signal']
            if 'bullish' in signal:
                scores.append(1 if 'strongly' in signal else 0.5)
            elif 'bearish' in signal:
                scores.append(-1 if 'strongly' in signal else -0.5)
            else:
                scores.append(0)
        
        # FII/DII bias
        if fii_dii:
            if fii_dii['fii_net'] > 500:
                scores.append(1)
            elif fii_dii['fii_net'] < -500:
                scores.append(-1)
            else:
                scores.append(0)
        
        avg_score = np.mean(scores) if scores else 0
        
        if avg_score > 0.3:
            return 'bullish'
        elif avg_score < -0.3:
            return 'bearish'
        else:
            return 'neutral'
    
    def _assess_risk_level(self, volatility, oi):
        """Assess current risk level"""
        risk_score = 0
        
        # VIX-based risk
        if volatility:
            vix = volatility['vix']
            if vix > 25:
                risk_score += 2
            elif vix > 20:
                risk_score += 1
        
        # OI-based risk
        if oi and 'pcr_oi' in oi:
            pcr = oi['pcr_oi']
            if pcr < 0.5 or pcr > 2.0:
                risk_score += 1
        
        if risk_score >= 2:
            return 'high'
        elif risk_score >= 1:
            return 'medium'
        else:
            return 'low'