import pandas as pd
import numpy as np

def calculate_indicators(df):
    df = df.copy()

    # Flatten multi-index columns if exist (e.g. yfinance)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(col).strip() for col in df.columns.values]

    # Rename columns for consistency
    rename_map = {
        "Adj Close": "Close",
        "Adj_Close": "Close",
        "Close": "Close",
        "High": "High",
        "Low": "Low",
        "Open": "Open",
        "Volume": "Volume"
    }
    df.rename(columns=lambda x: rename_map.get(x, x), inplace=True)

    # Check necessary columns exist
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Calculate EMAs
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["EMA200"] = df["Close"].ewm(span=200, adjust=False).mean()

    # Bollinger Bands
    rolling_mean = df["Close"].rolling(window=20).mean()
    rolling_std = df["Close"].rolling(window=20).std()
    df["BB_Mid"] = rolling_mean
    df["BB_Upper"] = rolling_mean + 2 * rolling_std
    df["BB_Lower"] = rolling_mean - 2 * rolling_std

    # RSI (14)
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # MACD (12, 26, 9)
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]

    # ATR (14)
    high_low = df["High"] - df["Low"]
    high_close_prev = (df["High"] - df["Close"].shift()).abs()
    low_close_prev = (df["Low"] - df["Close"].shift()).abs()
    tr = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
    df["ATR"] = tr.rolling(window=14).mean()

    return df

def generate_signal(df, rr_ratio=2, atr_multiplier=1.5):
    last = df.iloc[-1]

    # Trend filter by EMA200
    price = last["Close"]
    ema200 = last["EMA200"]

    if pd.isna(price) or pd.isna(ema200):
        return "Not enough data to generate signal."

    is_bull = price > ema200
    is_bear = price < ema200

    rsi = last["RSI"]
    macd = last["MACD"]
    macd_signal = last["MACD_Signal"]

    atr = last["ATR"]

    if pd.isna(rsi) or pd.isna(macd) or pd.isna(macd_signal) or pd.isna(atr):
        return "Not enough data to generate signal."

    # Simple logic for demonstration:
    if is_bull and rsi > 50 and macd > macd_signal:
        sl = price - atr * atr_multiplier
        tp = price + (price - sl) * rr_ratio
        return f"BUY signal\nStop Loss: {sl:.5f}\nTake Profit: {tp:.5f}"
    elif is_bear and rsi < 50 and macd < macd_signal:
        sl = price + atr * atr_multiplier
        tp = price - (sl - price) * rr_ratio
        return f"SELL signal\nStop Loss: {sl:.5f}\nTake Profit: {tp:.5f}"
    else:
        return "No clear signal."
