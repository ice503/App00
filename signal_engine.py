import pandas as pd
import numpy as np

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate core technical indicators for trading signals."""

    # Ensure correct column names and single-level columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.copy()
    df = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)

    # Moving Averages
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["EMA200"] = df["Close"].ewm(span=200, adjust=False).mean()

    # Bollinger Bands
    df["BB_Mid"] = df["Close"].rolling(window=20).mean()
    rolling_std = df["Close"].rolling(window=20).std()
    df["BB_Upper"] = df["BB_Mid"] + 2 * rolling_std
    df["BB_Lower"] = df["BB_Mid"] - 2 * rolling_std

    # RSI (manual calculation to avoid 2D errors)
    delta = df["Close"].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain, index=df.index).rolling(window=14).mean()
    avg_loss = pd.Series(loss, index=df.index).rolling(window=14).mean()

    rs = avg_gain / (avg_loss + 1e-10)  # prevent divide by zero
    df["RSI"] = 100 - (100 / (1 + rs))

    # ATR (Average True Range)
    high_low = df["High"] - df["Low"]
    high_close = np.abs(df["High"] - df["Close"].shift())
    low_close = np.abs(df["Low"] - df["Close"].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["ATR"] = tr.rolling(window=14).mean()

    # Pivot Points (classic)
    df["Pivot"] = (df["High"] + df["Low"] + df["Close"]) / 3
    df["R1"] = 2 * df["Pivot"] - df["Low"]
    df["S1"] = 2 * df["Pivot"] - df["High"]

    return df


def generate_signals(df: pd.DataFrame, rr_ratio=2, atr_multiplier=1.5) -> pd.DataFrame:
    """Generate Buy/Sell signals with Stop Loss & Take Profit."""

    df = df.copy()
    df["Signal"] = ""
    df["StopLoss"] = np.nan
    df["TakeProfit"] = np.nan

    for i in range(1, len(df)):
        price = df["Close"].iloc[i]
        ema20 = df["EMA20"].iloc[i]
        ema200 = df["EMA200"].iloc[i]
        rsi = df["RSI"].iloc[i]
        atr = df["ATR"].iloc[i]

        if price > ema200 and price > ema20 and rsi > 50:
            df.at[df.index[i], "Signal"] = "BUY"
            df.at[df.index[i], "StopLoss"] = price - atr_multiplier * atr
            df.at[df.index[i], "TakeProfit"] = price + rr_ratio * atr_multiplier * atr

        elif price < ema200 and price < ema20 and rsi < 50:
            df.at[df.index[i], "Signal"] = "SELL"
            df.at[df.index[i], "StopLoss"] = price + atr_multiplier * atr
            df.at[df.index[i], "TakeProfit"] = price - rr_ratio * atr_multiplier * atr

    return df
