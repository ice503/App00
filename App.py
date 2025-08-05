import pandas as pd
import numpy as np

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate all indicators safely and prevent empty DataFrame issues."""
    if df.empty:
        raise ValueError("Downloaded data is empty. Check the symbol or interval.")

    # Reset index to ensure numeric indexing
    df = df.copy().reset_index(drop=True)

    # Ensure required columns exist
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # --- Moving Averages ---
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["EMA200"] = df["Close"].ewm(span=200, adjust=False).mean()

    # --- Bollinger Bands ---
    df["BB_Mid"] = df["Close"].rolling(window=20).mean()
    rolling_std = df["Close"].rolling(window=20).std()
    df["BB_Upper"] = df["BB_Mid"] + (2 * rolling_std)
    df["BB_Lower"] = df["BB_Mid"] - (2 * rolling_std)

    # --- RSI ---
    delta = df["Close"].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    gain_series = pd.Series(gain.flatten() if gain.ndim > 1 else gain)
    loss_series = pd.Series(loss.flatten() if loss.ndim > 1 else loss)

    avg_gain = gain_series.rolling(window=14).mean()
    avg_loss = loss_series.rolling(window=14).mean()
    rs = avg_gain / (avg_loss.replace(0, np.nan))
    df["RSI"] = 100 - (100 / (1 + rs))

    # --- ATR (Average True Range) ---
    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close = (df["Low"] - df["Close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["ATR"] = tr.rolling(window=14).mean()

    # --- Pivot Points (Daily style) ---
    df["Pivot"] = (df["High"] + df["Low"] + df["Close"]) / 3
    df["R1"] = 2 * df["Pivot"] - df["Low"]
    df["S1"] = 2 * df["Pivot"] - df["High"]

    # Drop only leading NaN rows, keep last row for signals
    df = df.dropna().reset_index(drop=True)

    if df.empty:
        raise ValueError("Indicators removed all rows. Use longer period or smaller indicators.")

    return df


def generate_signal(df: pd.DataFrame, rr_ratio: float = 2.0, atr_multiplier: float = 1.5) -> str:
    """Generate buy/sell signal based on last row of indicators."""
    if df.empty:
        return "No data available to generate signal."

    last = df.iloc[-1]

    # Required indicators
    required_cols = ["Close", "EMA20", "EMA50", "EMA200", "RSI", "ATR"]
    for col in required_cols:
        if col not in df.columns:
            return f"Missing required column for signal: {col}"
        if pd.isna(last[col]):
            return "Not enough data to generate signal yet."

    price = last["Close"]
    ema20, ema50, ema200 = last["EMA20"], last["EMA50"], last["EMA200"]
    rsi = last["RSI"]
    atr = last["ATR"]

    signal = "No trade"
    stop_loss, take_profit = None, None

    # --- Buy Signal ---
    if price > ema200 and ema20 > ema50 and rsi > 50:
        signal = "BUY"
        stop_loss = price - (atr * atr_multiplier)
        take_profit = price + (atr * atr_multiplier * rr_ratio)

    # --- Sell Signal ---
    elif price < ema200 and ema20 < ema50 and rsi < 50:
        signal = "SELL"
        stop_loss = price + (atr * atr_multiplier)
        take_profit = price - (atr * atr_multiplier * rr_ratio)

    return f"""
Signal: {signal}
Price: {price:.5f}
Stop Loss: {stop_loss:.5f if stop_loss else 0}
Take Profit: {take_profit:.5f if take_profit else 0}
"""
