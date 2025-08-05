import pandas as pd
import numpy as np

def calculate_indicators(df):
    df = df.copy()

    # --- Trend Indicators (EMA) ---
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["EMA200"] = df["Close"].ewm(span=200, adjust=False).mean()

    # --- Bollinger Bands ---
    df["BB_Mid"] = df["Close"].rolling(window=20).mean()
    rolling_std = df["Close"].rolling(window=20).std()
    df["BB_Upper"] = df["BB_Mid"] + 2 * rolling_std
    df["BB_Lower"] = df["BB_Mid"] - 2 * rolling_std

    # --- RSI Calculation (14) ---
    delta = df["Close"].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=14).mean()
    avg_loss = pd.Series(loss).rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # --- MACD (12,26,9) ---
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]

    # --- ATR (14) ---
    df["H-L"] = df["High"] - df["Low"]
    df["H-C"] = np.abs(df["High"] - df["Close"].shift())
    df["L-C"] = np.abs(df["Low"] - df["Close"].shift())
    tr = df[["H-L", "H-C", "L-C"]].max(axis=1)
    df["ATR"] = tr.rolling(window=14).mean()

    # --- Pivot Points (Classic) ---
    df["Pivot"] = (df["High"] + df["Low"] + df["Close"]) / 3
    df["R1"] = 2 * df["Pivot"] - df["Low"]
    df["S1"] = 2 * df["Pivot"] - df["High"]
    df["R2"] = df["Pivot"] + (df["High"] - df["Low"])
    df["S2"] = df["Pivot"] - (df["High"] - df["Low"])

    # --- Volume Analysis (Simple Breakout Check) ---
    df["Vol_MA20"] = df["Volume"].rolling(window=20).mean()
    df["Vol_Breakout"] = df["Volume"] > df["Vol_MA20"] * 1.5

    return df


def generate_signal(df, rr_ratio=2.0, atr_multiplier=1.5):
    last = df.iloc[-1]

    # --- Determine Trend ---
    if last["EMA20"] > last["EMA50"] and last["EMA50"] > last["EMA200"]:
        trend = "Bullish"
    elif last["EMA20"] < last["EMA50"] and last["EMA50"] < last["EMA200"]:
        trend = "Bearish"
    else:
        trend = "Sideways"

    # --- Signal Logic ---
    signal = "Hold"
    reason = "No clear signal"
    confidence = 50

    if trend == "Bullish" and last["RSI"] > 50 and last["MACD"] > last["MACD_Signal"]:
        signal = "Buy"
        reason = "Uptrend with RSI > 50 and MACD bullish"
        confidence = 80
        if last["Vol_Breakout"]:
            confidence += 10

    elif trend == "Bearish" and last["RSI"] < 50 and last["MACD"] < last["MACD_Signal"]:
        signal = "Sell"
        reason = "Downtrend with RSI < 50 and MACD bearish"
        confidence = 80
        if last["Vol_Breakout"]:
            confidence += 10

    # --- Stop-Loss & Take-Profit Suggestion ---
    entry_price = last["Close"]
    atr = last["ATR"]
    stop_loss = None
    take_profit = None

    if signal == "Buy":
        stop_loss = entry_price - atr * atr_multiplier
        take_profit = entry_price + (entry_price - stop_loss) * rr_ratio
    elif signal == "Sell":
        stop_loss = entry_price + atr * atr_multiplier
        take_profit = entry_price - (stop_loss - entry_price) * rr_ratio

    return {
        "signal": signal,
        "entry": entry_price,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "confidence": confidence,
        "reason": reason
}
