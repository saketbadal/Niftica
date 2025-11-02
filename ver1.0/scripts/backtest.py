# scripts/backtest.py
#!/usr/bin/env python3
"""
Backtest the recommendation system with historical data
"""
import pandas as pd
from datetime import datetime, timedelta
from scanner.data_fetcher import DataFetcher
from scanner.signal_processor import SignalProcessor
from utils.logging_setup import logger

class Backtester:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.data_fetcher = DataFetcher()
        self.signal_processor = SignalProcessor()
        self.results = []
    
    def run_backtest(self, symbol):
        """Run backtest for a symbol"""
        print(f"Running backtest for {symbol} from {self.start_date} to {self.end_date}")
        
        current_date = self.start_date
        
        while current_date <= self.end_date:
            # Skip weekends
            if current_date.weekday() >= 5:
                current_date += timedelta(days=1)
                continue
            
            # Fetch data up to current date
            df = self._fetch_historical_data(symbol, current_date)
            
            if df is not None and len(df) >= 100:
                # Get LTP
                ltp = df['close'].iloc[-1]
                
                # Calculate indicators
                technical_data = self.signal_processor._calculate_technicals(df, ltp)
                
                if technical_data and self.signal_processor._check_signal_conditions(symbol, technical_data):
                    # Record signal
                    self.results.append({
                        'date': current_date,
                        'symbol': symbol,
                        'signal': 'BUY' if technical_data['both_bullish'] else 'SELL',
                        'price': ltp,
                        'st_10_1': technical_data['st_10_1']['value'],
                        'st_10_3': technical_data['st_10_3']['value'],
                        'adx': technical_data.get('adx', 0)
                    })
            
            # Move to next day
            current_date += timedelta(days=1)
        
        return self.results
    
    def _fetch_historical_data(self, symbol, end_date):
        """Fetch historical data up to a specific date"""
        # This is a simplified version - implement proper historical data fetching
        try:
            # Fetch last 10 days of data
            from_date = end_date - timedelta(days=10)
            
            # Use your data fetching logic here
            # For now, returning None as placeholder
            return None
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return None
    
    def analyze_results(self):
        """Analyze backtest results"""
        if not self.results:
            print("No signals generated during backtest period")
            return
        
        df = pd.DataFrame(self.results)
        
        print(f"\nBacktest Results:")
        print(f"Total Signals: {len(df)}")
        print(f"Buy Signals: {len(df[df['signal'] == 'BUY'])}")
        print(f"Sell Signals: {len(df[df['signal'] == 'SELL'])}")
        
        # Save to CSV
        filename = f"backtest_results_{self.start_date.strftime('%Y%m%d')}_{self.end_date.strftime('%Y%m%d')}.csv"
        df.to_csv(filename, index=False)
        print(f"\nResults saved to: {filename}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Backtest the recommendation system')
    parser.add_argument('symbol', help='Symbol to backtest (e.g., NIFTY24D1925000CE)')
    parser.add_argument('--start', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', required=True, help='End date (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    start_date = datetime.strptime(args.start, '%Y-%m-%d')
    end_date = datetime.strptime(args.end, '%Y-%m-%d')
    
    backtester = Backtester(start_date, end_date)
    backtester.run_backtest(args.symbol)
    backtester.analyze_results()