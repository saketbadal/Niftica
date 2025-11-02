# data_enrichment/oi_analyzer.py
import pandas as pd
import numpy as np
from utils.logging_setup import logger
from scanner.data_fetcher import DataFetcher

class OIAnalyzer:
    def __init__(self):
        self.fetcher = DataFetcher()
        
    def fetch_option_chain(self, spot_price, expiry_date):
        """Fetch and analyze option chain"""
        try:
            strikes = self._get_relevant_strikes(spot_price)
            option_data = []
            
            for strike in strikes:
                # Fetch CE data
                ce_symbol = f"NIFTY{expiry_date}{int(strike)}CE"
                ce_quote = self.fetcher.get_quote(ce_symbol)
                if ce_quote:
                    ce_data = self._extract_option_data(ce_symbol, ce_quote, "CE", strike)
                    if ce_data:
                        option_data.append(ce_data)
                
                # Fetch PE data
                pe_symbol = f"NIFTY{expiry_date}{int(strike)}PE"
                pe_quote = self.fetcher.get_quote(pe_symbol)
                if pe_quote:
                    pe_data = self._extract_option_data(pe_symbol, pe_quote, "PE", strike)
                    if pe_data:
                        option_data.append(pe_data)
            
            df = pd.DataFrame(option_data)
            return self._analyze_oi_data(df, spot_price)
            
        except Exception as e:
            logger.error(f"Error fetching option chain: {e}")
            return None
    
    def _get_relevant_strikes(self, spot_price, num_strikes=10):
        """Get relevant strike prices around spot"""
        base = 50  # Nifty strikes are in multiples of 50
        atm_strike = round(spot_price / base) * base
        
        strikes = []
        for i in range(-num_strikes, num_strikes + 1):
            strike = atm_strike + (i * base)
            strikes.append(strike)
        
        return strikes
    
    def _extract_option_data(self, symbol, quote_data, option_type, strike):
        """Extract relevant data from quote"""
        try:
            key = list(quote_data.keys())[0]
            data = quote_data[key]
            
            return {
                'symbol': symbol,
                'strike': strike,
                'type': option_type,
                'ltp': data.get('last_price', 0),
                'volume': data.get('volume', 0),
                'oi': data.get('oi', 0),
                'oi_day_high': data.get('oi_day_high', 0),
                'oi_day_low': data.get('oi_day_low', 0),
                'bid': data.get('depth', {}).get('buy', [{}])[0].get('price', 0),
                'ask': data.get('depth', {}).get('sell', [{}])[0].get('price', 0),
            }
        except Exception as e:
            logger.error(f"Error extracting option data: {e}")
            return None
    
    def _analyze_oi_data(self, df, spot_price):
        """Analyze OI data for insights"""
        if df.empty:
            return None
            
        # Separate CE and PE data
        ce_df = df[df['type'] == 'CE'].copy()
        pe_df = df[df['type'] == 'PE'].copy()
        
        # Calculate OI change
        ce_df['oi_change'] = ce_df['oi'] - ce_df['oi_day_low']
        pe_df['oi_change'] = pe_df['oi'] - pe_df['oi_day_low']
        
        # Calculate PCR
        total_pe_oi = pe_df['oi'].sum()
        total_ce_oi = ce_df['oi'].sum()
        pcr_oi = total_pe_oi / total_ce_oi if total_ce_oi > 0 else 1
        
        # Find max OI strikes
        max_ce_oi_strike = ce_df.loc[ce_df['oi'].idxmax(), 'strike'] if not ce_df.empty else spot_price
        max_pe_oi_strike = pe_df.loc[pe_df['oi'].idxmax(), 'strike'] if not pe_df.empty else spot_price
        
        # Analyze OI buildups
        ce_buildup = ce_df[ce_df['oi_change'] > 1000].sort_values('oi_change', ascending=False)
        pe_buildup = pe_df[pe_df['oi_change'] > 1000].sort_values('oi_change', ascending=False)
        
        # Calculate support and resistance
        resistance_levels = ce_df.nlargest(3, 'oi')[['strike', 'oi']].values.tolist()
        support_levels = pe_df.nlargest(3, 'oi')[['strike', 'oi']].values.tolist()
        
        analysis = {
            'pcr_oi': round(pcr_oi, 3),
            'max_ce_oi_strike': max_ce_oi_strike,
            'max_pe_oi_strike': max_pe_oi_strike,
            'resistance_levels': resistance_levels,
            'support_levels': support_levels,
            'ce_buildup_count': len(ce_buildup),
            'pe_buildup_count': len(pe_buildup),
            'interpretation': self._interpret_oi(pcr_oi, spot_price, max_ce_oi_strike, max_pe_oi_strike)
        }
        
        return analysis
    
    def _interpret_oi(self, pcr, spot, ce_max, pe_max):
        """Interpret OI data"""
        bias = "neutral"
        confidence = 0.5
        reasoning = []
        
        # PCR interpretation
        if pcr < 0.7:
            bias = "bearish"
            confidence *= 0.8
            reasoning.append(f"Low PCR ({pcr:.2f}) indicates bearish sentiment")
        elif pcr > 1.3:
            bias = "bullish"
            confidence *= 1.2
            reasoning.append(f"High PCR ({pcr:.2f}) indicates bullish sentiment")
        
        # Support/Resistance interpretation
        if spot < pe_max:
            if bias == "bullish":
                confidence *= 1.1
            reasoning.append(f"Spot below max PE OI strike ({pe_max}) suggests support")
        elif spot > ce_max:
            if bias == "bearish":
                confidence *= 1.1
            reasoning.append(f"Spot above max CE OI strike ({ce_max}) suggests resistance")
        
        return {
            'bias': bias,
            'confidence': min(confidence, 1.0),
            'reasoning': reasoning
        }