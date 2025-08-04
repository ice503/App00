import pandas as pd
import numpy as np

def calculate_indicators(df):
    """Calculate all core indicators for trading signals."""
    df = df.copy()

    # 1. Flatten columns if Yahoo Finance returns multi-index
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

    # 2. Ensure numeric Series
    for col in ["Open", "High", "Low", "Close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 3. EMA (Trend)
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["EMA200"] = df["Close"].ewm(span=200, adjust=False).mean()

    # 4. MACD
    short_ema = df["Close"].ewm(span=12, adjust=False).mean()
    long_ema = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = short_ema - long_ema
    df["MACD_signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

    # 5. Bollinger Bands
    close_series = df["Close"].squeeze()
    df["BB_Mid"] = close_series.rolling(window=20).mean()
    rolling_std = close_series.rolling(window=20).std()
    df["BB_Upper"] = df["BB_Mid"] + 2 * rolling_std
    df["BB_Lower"] = df["BB_Mid"] - 2 * rolling_std

    # 6. ATR (Volatility)
    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close = (df["Low"] - df["Close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["ATR"] = tr.rolling(window=14).mean()

    # 7. RSI (Momentum)
    delta = close_series.diff().fillna(0)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    gain = pd.Series(gain, index=df.index)
    loss = pd.Series(loss, index=df.index)
    avg_gain = gain.rolling(window=14, min_periods=14).mean()
    avg_loss = loss.rolling(window=14, min_periods=14).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["RSI"] = 100 - (100 / (1 + rs))

    return df


def generate_signal(df, rr_ratio=2.0, atr_multiplier=1.5):
    """Generate trading signals with stop-loss and take-profit suggestions."""
    last = df.iloc[-1]
    price = last["Close"]
    atr = last["ATR"]

    signal = "HOLD"
    reason = "No strong signal"
    confidence = 50

    # --- Example Signal Logic ---
    if last["EMA20"] > last["EMA50"] and last["RSI"] > 55:
        signal = "BUY"
        reason = "EMA20 > EMA50 and RSI strong"
        confidence = 80
    elif last["EMA20"] < last["EMA50"] and last["RSI"] < 45:
        signal = "SELL"
        reason = "EMA20 < EMA50 and RSI weak"
        confidence = 80

    # Stop Loss & Take Profit
    if signal == "BUY":
        stop_loss = price - atr * atr_multiplier
        take_profit = price + (price - stop_loss) * rr_ratio
    elif signal == "SELL":
        stop_loss = price + atr * atr_multiplier
        take_profit = price - (stop_loss - price) * rr_ratio
    else:
        stop_loss = None
        take_profit = None

    return {
        "signal": signal,
        "confidence": confidence,
        "entry": price,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "reason": reason,
        }
