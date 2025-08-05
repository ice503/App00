import pandas as pd
import numpy as np
import ta  # make sure ta-lib or ta package is installed

def calculate_indicators(df):
    df = df.copy()

    # Flatten multi-index columns if any (common with yfinance)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]

    # Rename 'Adj Close' to 'Close' if present
    if "Adj Close" in df.columns:
        df.rename(columns={"Adj Close": "Close"}, inplace=True)

    # Check required columns
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Calculate EMA
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["EMA200"] = df["Close"].ewm(span=200, adjust=False).mean()

    # MACD using ta library
    macd = ta.trend.MACD(df["Close"], window_slow=26, window_fast=12, window_sign=9)
    df["MACD"] = macd.macd()
    df["MACD_Signal"] = macd.macd_signal()
    df["MACD_Hist"] = macd.macd_diff()

    # RSI
    rsi_indicator = ta.momentum.RSIIndicator(df["Close"], window=14)
    df["RSI"] = rsi_indicator.rsi()

    # Bollinger Bands
    df["BB_Mid"] = df["Close"].rolling(window=20).mean()
    rolling_std = df["Close"].rolling(window=20).std()
    df["BB_Upper"] = df["BB_Mid"] + 2 * rolling_std
    df["BB_Lower"] = df["BB_Mid"] - 2 * rolling_std

    # ATR
    atr_indicator = ta.volatility.AverageTrueRange(df["High"], df["Low"], df["Close"], window=14)
    df["ATR"] = atr_indicator.average_true_range()

    # Pivot Points (Classic)
    df["Pivot"] = (df["High"] + df["Low"] + df["Close"]) / 3
    df["R1"] = 2 * df["Pivot"] - df["Low"]
    df["S1"] = 2 * df["Pivot"] - df["High"]
    df["R2"] = df["Pivot"] + (df["High"] - df["Low"])
    df["S2"] = df["Pivot"] - (df["High"] - df["Low"])

    return df

def generate_signal(df, rr_ratio=2, atr_multiplier=1.5):
    # Use the last row for signal
    last = df.iloc[-1]

    required_cols = ["EMA200", "EMA50", "EMA20", "RSI", "MACD", "MACD_Signal", "ATR", "Close"]

    # Validate presence and non-null values
    for col in required_cols:
        if col not in df.columns or pd.isna(last[col]):
            return "Insufficient data for signal generation."

    price = last["Close"]
    ema200 = last["EMA200"]
    ema50 = last["EMA50"]
    ema20 = last["EMA20"]
    rsi = last["RSI"]
    macd = last["MACD"]
    macd_signal = last["MACD_Signal"]
    atr = last["ATR"]

    signal = None
    stop_loss = None
    take_profit = None

    # Example buy signal logic
    if price > ema200 and ema20 > ema50 and rsi > 50 and macd > macd_signal:
        signal = "BUY"
        stop_loss = price - atr_multiplier * atr
        take_profit = price + rr_ratio * (price - stop_loss)

    # Example sell signal logic
    elif price < ema200 and ema20 < ema50 and rsi < 50 and macd < macd_signal:
        signal = "SELL"
        stop_loss = price + atr_multiplier * atr
        take_profit = price - rr_ratio * (stop_loss - price)
    else:
        signal = "HOLD"

    return {
        "signal": signal,
        "stop_loss": round(stop_loss, 5) if stop_loss else None,
        "take_profit": round(take_profit, 5) if take_profit else None,
    }
