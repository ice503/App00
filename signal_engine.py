import pandas as pd
import numpy as np

def calculate_indicators(df):
    df = df.copy()

    # EMAs
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()

    # Bollinger Bands
    sma20 = df['Close'].rolling(window=20).mean()
    std20 = df['Close'].rolling(window=20).std()
    df['BB_upper'] = sma20 + (std20 * 2)
    df['BB_lower'] = sma20 - (std20 * 2)

    # RSI (manual to avoid shape errors)
    delta = df['Close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=14).mean()
    avg_loss = pd.Series(loss).rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_hist'] = df['MACD'] - df['MACD_signal']

    # ATR for SL/TP
    df['H-L'] = df['High'] - df['Low']
    df['H-C'] = abs(df['High'] - df['Close'].shift(1))
    df['L-C'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['H-L', 'H-C', 'L-C']].max(axis=1)
    df['ATR'] = df['TR'].rolling(window=14).mean()

    return df.dropna()

def generate_signal(df, rr_ratio=2.0, atr_multiplier=1.5):
    last = df.iloc[-1]
    price = last['Close']
    atr = last['ATR']

    signal = "HOLD"
    reason = []
    confidence = 0

    # Trend filter: EMA alignment
    if last['EMA20'] > last['EMA50'] > last['EMA200']:
        trend = "Bullish"
        confidence += 30
    elif last['EMA20'] < last['EMA50'] < last['EMA200']:
        trend = "Bearish"
        confidence += 30
    else:
        trend = "Sideways"

    # MACD confirmation
    if last['MACD'] > last['MACD_signal']:
        macd_signal = "Bullish"
        confidence += 20
    else:
        macd_signal = "Bearish"
        confidence += 20

    # RSI
    if last['RSI'] > 50:
        rsi_signal = "Bullish"
        confidence += 20
    else:
        rsi_signal = "Bearish"
        confidence += 20

    # Bollinger Band confirmation
    if price <= last['BB_lower']:
        reason.append("Oversold (Bollinger)")
        confidence += 10
    elif price >= last['BB_upper']:
        reason.append("Overbought (Bollinger)")
        confidence += 10

    # Generate final signal
    if trend == "Bullish" and macd_signal == "Bullish" and rsi_signal == "Bullish":
        signal = "BUY"
        reason.append("All indicators aligned for bullish setup")
    elif trend == "Bearish" and macd_signal == "Bearish" and rsi_signal == "Bearish":
        signal = "SELL"
        reason.append("All indicators aligned for bearish setup")

    # Risk Management
    stop_loss = price - atr * atr_multiplier if signal == "BUY" else price + atr * atr_multiplier
    take_profit = price + (atr * atr_multiplier * rr_ratio) if signal == "BUY" else price - (atr * atr_multiplier * rr_ratio)

    return {
        "signal": signal,
        "confidence": min(confidence, 100),
        "entry": round(price, 5),
        "stop_loss": round(stop_loss, 5),
        "take_profit": round(take_profit, 5),
        "reason": ", ".join(reason) if reason else "No strong confluence"
    }
