import pandas as pd
import ta
import numpy as np

def calculate_indicators(df):
    df = df.copy()

    # EMAs
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['EMA200'] = df['Close'].ewm(span=200).mean()

    # MACD with fix for 1D array
    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = np.ravel(macd.macd().values)
    df['MACD_signal'] = np.ravel(macd.macd_signal().values)

    # RSI
    rsi_indicator = ta.momentum.RSIIndicator(df['Close'], window=14)
    df['RSI'] = rsi_indicator.rsi()

    # ATR
    atr = ta.volatility.AverageTrueRange(
        high=df['High'], low=df['Low'], close=df['Close'], window=14
    )
    df['ATR'] = atr.average_true_range()

    # Bollinger Bands
    bb = ta.volatility.BollingerBands(df['Close'], window=20, window_dev=2)
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_lower'] = bb.bollinger_lband()

    return df

def generate_signal(df, rr_ratio=2, atr_multiplier=1.5):
    last = df.iloc[-1]

    # Safety checks: if any required indicator is missing or NaN, return WAIT
    required_cols = ['Close', 'EMA200', 'MACD', 'MACD_signal', 'RSI', 'ATR']
    if any(col not in df.columns or pd.isna(last[col]) for col in required_cols):
        return {
            "signal": "WAIT",
            "confidence": 50,
            "entry": None,
            "stop_loss": None,
            "take_profit": None,
            "reason": "Insufficient data for signal calculation"
        }

    signal = "WAIT"
    confidence = 50
    entry = last['Close']

    # Buy Signal
    if last['Close'] > last['EMA200'] and last['MACD'] > last['MACD_signal'] and last['RSI'] > 50:
        signal = "BUY"
        confidence = 70
        sl = entry - (last['ATR'] * atr_multiplier)
        tp = entry + (last['ATR'] * atr_multiplier * rr_ratio)

    # Sell Signal
    elif last['Close'] < last['EMA200'] and last['MACD'] < last['MACD_signal'] and last['RSI'] < 50:
        signal = "SELL"
        confidence = 70
        sl = entry + (last['ATR'] * atr_multiplier)
        tp = entry - (last['ATR'] * atr_multiplier * rr_ratio)

    else:
        sl, tp = None, None

    return {
        "signal": signal,
        "confidence": confidence,
        "entry": round(entry, 5) if entry is not None else None,
        "stop_loss": round(sl, 5) if sl else None,
        "take_profit": round(tp, 5) if tp else None,
        "reason": f"EMA200 trend + MACD + RSI alignment ({signal})"
    }
