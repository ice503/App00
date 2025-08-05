import pandas as pd
import numpy as np

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # EMA Indicators
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["EMA200"] = df["Close"].ewm(span=200, adjust=False).mean()

    # Bollinger Bands
    rolling_mean = df["Close"].rolling(window=20).mean()
    rolling_std = df["Close"].rolling(window=20).std()
    df["BB_Mid"] = rolling_mean
    df["BB_Upper"] = rolling_mean + (2 * rolling_std)
    df["BB_Lower"] = rolling_mean - (2 * rolling_std)

    # RSI Calculation
    delta = df["Close"].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(window=14).mean()
    avg_loss = pd.Series(loss).rolling(window=14).mean()

    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # ATR Calculation
    df["H-L"] = df["High"] - df["Low"]
    df["H-C"] = abs(df["High"] - df["Close"].shift())
    df["L-C"] = abs(df["Low"] - df["Close"].shift())
    df["TR"] = df[["H-L", "H-C", "L-C"]].max(axis=1)
    df["ATR"] = df["TR"].rolling(window=14).mean()

    df.dropna(inplace=True)
    return df

def generate_signal(df: pd.DataFrame, rr_ratio=2.0, atr_multiplier=1.5):
    last = df.iloc[-1]

    if last["Close"] > last["EMA200"] and last["RSI"] > 50:
        signal = "BUY"
        stop_loss = last["Close"] - (last["ATR"] * atr_multiplier)
        take_profit = last["Close"] + (last["ATR"] * atr_multiplier * rr_ratio)
    elif last["Close"] < last["EMA200"] and last["RSI"] < 50:
        signal = "SELL"
        stop_loss = last["Close"] + (last["ATR"] * atr_multiplier)
        take_profit = last["Close"] - (last["ATR"] * atr_multiplier * rr_ratio)
    else:
        signal = "HOLD"
        stop_loss = None
        take_profit = None

    return {
        "Signal": signal,
        "Last Price": round(last["Close"], 5),
        "Stop Loss": round(stop_loss, 5) if stop_loss else None,
        "Take Profit": round(take_profit, 5) if take_profit else None
    }
