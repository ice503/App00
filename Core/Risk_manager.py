import pandas as pd
import ta

def calculate_risk_levels(df: pd.DataFrame, entry_price: float, risk_ratio: float = 2.0):
    """Calculate stop-loss and take-profit using ATR."""
    atr = ta.volatility.AverageTrueRange(
        df['high'], df['low'], df['close']
    ).average_true_range().iloc[-1]
    
    stop_loss = entry_price - atr
    take_profit = entry_price + atr * risk_ratio
    return stop_loss, take_profit
