import pandas as pd
import numpy as np

def calculate_indicators(df):
    df = df.copy()

    # ========================
    # Moving Averages
    # ========================
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()

    # ========================
    # MACD (Manual)
    # ========================
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # ========================
    # RSI (Manual)
    # ========================
    delta = df['Close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    roll_up = pd.Series(gain).rolling(window=14).mean()
    roll_down = pd.Series(loss).rolling(window=14).mean()

    rs = roll_up / (roll_down + 1e-10)
    df['RSI'] = 100 - (100 / (1 + rs))

    # ========================
    # ATR (Manual)
    # ========================
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR'] = tr.rolling(window=14).mean()

    # ========================
    # Bollinger Bands
    # ========================
    df['BB_upper'] = df['Close'].rolling(window=20).mean() + 2 * df['Close'].rolling(window=20).std()
    df['BB_lower'] = df['Close'].rolling(window=20).mean() - 2 * df['Close'].rolling(window=20).std()

    return df

def generate_signal(df, rr_ratio=2, atr_multiplier=1.5):
    last = df.iloc[-1]

    # Safety check
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
