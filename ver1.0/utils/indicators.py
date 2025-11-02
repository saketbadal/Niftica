# utils/indicators.py
import numpy as np
import pandas as pd
from utils.logging_setup import logger

def calculate_supertrend(df, period=10, multiplier=3):
    """Calculate SuperTrend indicator"""
    if df is None or len(df) < period:
        logger.warning(f"Insufficient data for SuperTrend calculation")
        return None
    
    try:
        df = df.copy()
        
        # Calculate True Range
        df['tr0'] = abs(df['high'] - df['low'])
        df['tr1'] = abs(df['high'] - df['close'].shift(1))
        df['tr2'] = abs(df['low'] - df['close'].shift(1))
        df['tr'] = df[['tr0', 'tr1', 'tr2']].max(axis=1)
        
        # Calculate ATR
        df['atr'] = df['tr'].rolling(window=period).mean()
        
        # Calculate bands
        hl_avg = (df['high'] + df['low']) / 2
        df['basic_upper'] = hl_avg + (multiplier * df['atr'])
        df['basic_lower'] = hl_avg - (multiplier * df['atr'])
        
        # Initialize columns
        df['final_upper'] = df['basic_upper']
        df['final_lower'] = df['basic_lower']
        df['supertrend'] = np.nan
        
        # Calculate SuperTrend
        for i in range(1, len(df)):
            # Final upper band
            if df['basic_upper'].iloc[i] < df['final_upper'].iloc[i-1] or df['close'].iloc[i-1] > df['final_upper'].iloc[i-1]:
                df.loc[df.index[i], 'final_upper'] = df['basic_upper'].iloc[i]
            else:
                df.loc[df.index[i], 'final_upper'] = df['final_upper'].iloc[i-1]
            
            # Final lower band
            if df['basic_lower'].iloc[i] > df['final_lower'].iloc[i-1] or df['close'].iloc[i-1] < df['final_lower'].iloc[i-1]:
                df.loc[df.index[i], 'final_lower'] = df['basic_lower'].iloc[i]
            else:
                df.loc[df.index[i], 'final_lower'] = df['final_lower'].iloc[i-1]
        
        # Determine SuperTrend
        df['supertrend'] = np.where(df['close'] > df['final_upper'], df['final_lower'], df['final_upper'])
        df['trend'] = np.where(df['close'] > df['supertrend'], 'bullish', 'bearish')
        
        return df
        
    except Exception as e:
        logger.error(f"Error calculating SuperTrend: {e}")
        return None

def calculate_adx(df, period=14):
    """Calculate Average Directional Index"""
    try:
        df = df.copy()
        
        # Calculate directional movement
        df['plus_dm'] = np.where((df['high'] - df['high'].shift(1)) > (df['low'].shift(1) - df['low']), 
                                 np.maximum(df['high'] - df['high'].shift(1), 0), 0)
        df['minus_dm'] = np.where((df['low'].shift(1) - df['low']) > (df['high'] - df['high'].shift(1)), 
                                  np.maximum(df['low'].shift(1) - df['low'], 0), 0)
        
        # Calculate TR
        df['tr'] = np.maximum(df['high'] - df['low'], 
                              np.maximum(abs(df['high'] - df['close'].shift(1)), 
                                        abs(df['low'] - df['close'].shift(1))))
        
        # Smooth the values
        df['smooth_plus_dm'] = df['plus_dm'].rolling(window=period).mean()
        df['smooth_minus_dm'] = df['minus_dm'].rolling(window=period).mean()
        df['smooth_tr'] = df['tr'].rolling(window=period).mean()
        
        # Calculate DI
        df['plus_di'] = 100 * (df['smooth_plus_dm'] / df['smooth_tr'])
        df['minus_di'] = 100 * (df['smooth_minus_dm'] / df['smooth_tr'])
        
        # Calculate DX and ADX
        df['dx'] = 100 * (abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di']))
        df['adx'] = df['dx'].rolling(window=period).mean()
        
        return df['adx'].iloc[-1]
        
    except Exception as e:
        logger.error(f"Error calculating ADX: {e}")
        return None