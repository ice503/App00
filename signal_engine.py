import pandas as pd
import numpy as np

def calculate_indicators(df):
    """
    Calculate all technical indicators for the dataframe.
    Required columns: Open, High, Low, Close, Volume
    """
    df = df.copy()

    # EMA Trend Indicators
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["EMA200"] = df["Close"].ewm(span=200, adjust=False).mean()

    # MACD
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

    # Bollinger Bands
    df["BB_Mid"] = df["Close"].rolling(window=20).mean()
    rolling_std = df["Close"].rolling(window=20).std()
    df["BB_Upper"] = df["BB_Mid"] + 2 * rolling_std
    df["BB_Lower"] = df["BB_Mid"] - 2 * rolling_std

    # ATR (Volatility)
    high_low = df["High"] - df["Low"]
    high_close = np.abs(df["High"] - df["Close"].shift())
    low_close = np.abs(df["Low"] - df["Close"].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    df["ATR"] = true_range.rolling(window=14).mean()

    # RSI (Manual to avoid 2D error)
    delta = df["Close"].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=14).mean()
    avg_loss = pd.Series(loss).rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # Pivot Points
    df["Pivot"] = (df["High"] + df["Low"] + df["Close"]) / 3
    df["R1"] = 2 * df["Pivot"] - df["Low"]
    df["S1"] = 2 * df["Pivot"] - df["High"]

    return df


def generate_signals(df, rr_ratio=2, atr_multiplier=1.5):
    """
    Generate Buy/Sell/Hold signals for all historical candles.
    Returns df with a new 'Signal' column.
    """
    df = df.copy()
    df["Signal"] = "HOLD"  # Default

    for i in range(len(df)):
        if i < 50:  # Wait for indicators to initialize
            continue

        price = df["Close"].iloc[i]
        ema20 = df["EMA20"].iloc[i]
        ema50 = df["EMA50"].iloc[i]
        ema200 = df["EMA200"].iloc[i]
        rsi = df["RSI"].iloc[i]
        atr = df["ATR"].iloc[i]

        # --- Buy Signal Logic ---
        if price > ema200 and ema20 > ema50 and rsi > 50 and rsi < 70:
            df["Signal"].iloc[i] = "BUY"

        # --- Sell Signal Logic ---
        elif price < ema200 and ema20 < ema50 and rsi < 50 and rsi > 30:
            df["Signal"].iloc[i] = "SELL"

        # Stop-loss and Take-profit can be calculated here if needed
        # Example for BUY
        if df["Signal"].iloc[i] == "BUY":
            df.loc[df.index[i], "StopLoss"] = price - atr * atr_multiplier
            df.loc[df.index[i], "TakeProfit"] = price + atr * atr_multiplier * rr_ratio
        elif df["Signal"].iloc[i] == "SELL":
            df.loc[df.index[i], "StopLoss"] = price + atr * atr_multiplier
            df.loc[df.index[i], "TakeProfit"] = price - atr * atr_multiplier * rr_ratio

    return df
