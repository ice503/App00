import pandas as pd
import numpy as np
import ta

def calculate_indicators(df):
    # Ensure required columns exist
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Calculate EMAs
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()

    # Calculate MACD
    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_Signal'] = macd.macd_signal()
    df['MACD_Hist'] = macd.macd_diff()

    # Calculate RSI
    rsi_indicator = ta.momentum.RSIIndicator(df['Close'], window=14)
    df['RSI'] = rsi_indicator.rsi()

    # Bollinger Bands
    df['BB_Mid'] = df['Close'].rolling(window=20).mean()
    rolling_std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Mid'] + 2 * rolling_std
    df['BB_Lower'] = df['BB_Mid'] - 2 * rolling_std

    # ATR
    atr = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close'], window=14)
    df['ATR'] = atr.average_true_range()

    # Pivot Points (Classic) daily
    df['Pivot'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['R1'] = 2 * df['Pivot'] - df['Low']
    df['S1'] = 2 * df['Pivot'] - df['High']
    df['R2'] = df['Pivot'] + (df['High'] - df['Low'])
    df['S2'] = df['Pivot'] - (df['High'] - df['Low'])

    return df


def generate_signal(df, rr_ratio=2.0, atr_multiplier=1.5):
    if df.empty or len(df) < 1:
        return {"signal": "No data to generate signal."}

    last = df.iloc[-1]

    # Check if necessary columns exist and last row values are valid
    required_cols = ['Close', 'EMA20', 'EMA50', 'EMA200', 'MACD', 'MACD_Signal', 'RSI', 'ATR', 'S1', 'R1']
    for col in required_cols:
        if col not in df.columns or pd.isna(last.get(col)):
            return {"signal": f"Insufficient data: missing or NaN {col}"}

    price = last['Close']
    ema20 = last['EMA20']
    ema50 = last['EMA50']
    ema200 = last['EMA200']
    macd = last['MACD']
    macd_signal = last['MACD_Signal']
    rsi = last['RSI']
    atr = last['ATR']
    support = last['S1']
    resistance = last['R1']

    signal = "Hold"
    entry = price
    stop_loss = None
    take_profit = None

    # Example buy signal condition
    if price > ema200 and ema20 > ema50 and macd > macd_signal and rsi > 50:
        signal = "Buy"
        # Stop loss 1.5x ATR below current price
        stop_loss = price - atr_multiplier * atr
        # Take profit based on risk reward ratio
        take_profit = price + rr_ratio * (price - stop_loss)

    # Example sell signal condition
    elif price < ema200 and ema20 < ema50 and macd < macd_signal and rsi < 50:
        signal = "Sell"
        stop_loss = price + atr_multiplier * atr
        take_profit = price - rr_ratio * (stop_loss - price)

    return {
        "signal": signal,
        "entry": entry,
        "stop_loss": round(stop_loss, 5) if stop_loss else None,
        "take_profit": round(take_profit, 5) if take_profit else None
    }
