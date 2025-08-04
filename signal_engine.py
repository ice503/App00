import pandas as pd
import ta

def calculate_indicators(df):
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['EMA200'] = df['Close'].ewm(span=200).mean()

    # MACD
    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()

    # RSI
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()

    # ATR
    df['ATR'] = ta.volatility.AverageTrueRange(
        high=df['High'], low=df['Low'], close=df['Close'], window=14
    ).average_true_range()

    # Bollinger Bands
    bb = ta.volatility.BollingerBands(df['Close'], window=20, window_dev=2)
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_lower'] = bb.bollinger_lband()

    return df

def generate_signal(df, rr_ratio=2, atr_multiplier=1.5):
    last = df.iloc[-1]
    signal = "WAIT"
    confidence = 50
    entry = last['Close']

    # Trend & Momentum Logic
    if last['Close'] > last['EMA200'] and last['MACD'] > last['MACD_signal'] and last['RSI'] > 50:
        signal = "BUY"
        confidence = 70
        sl = entry - (last['ATR'] * atr_multiplier)
        tp = entry + (last['ATR'] * atr_multiplier * rr_ratio)
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
        "entry": round(entry, 5),
        "stop_loss": round(sl, 5) if sl else None,
        "take_profit": round(tp, 5) if tp else None,
        "reason": f"EMA200 trend + MACD + RSI alignment ({signal})"
      }
