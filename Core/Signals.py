import pandas as pd
import ta

def generate_signal(df: pd.DataFrame) -> str:
    """Generate a simple RSI-based trading signal."""
    df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
    latest_rsi = df['rsi'].iloc[-1]
    if latest_rsi < 30:
        return "BUY"
    elif latest_rsi > 70:
        return "SELL"
    return "HOLD"
