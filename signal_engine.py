def generate_signal(df):
    last = df.iloc[-1]
    price = float(last['Close'])
    ema20, ema50, ema200 = last['EMA20'], last['EMA50'], last['EMA200']
    macd, macd_signal = last['MACD'], last['MACD_Signal']
    rsi = last['RSI']
    atr = last['ATR']
    bb_upper, bb_lower = last['BB_Upper'], last['BB_Lower']

    signal = None
    confidence = 0

    # --- Trend Check ---
    if price > ema200:
        trend = "Uptrend"
        confidence += 1
    else:
        trend = "Downtrend"
        confidence += 1

    # --- EMA Cross ---
    if ema20 > ema50:
        ema_signal = "Bullish (EMA20 > EMA50)"
        confidence += 1
    else:
        ema_signal = "Bearish (EMA20 < EMA50)"
        confidence += 1

    # --- MACD ---
    macd_signal_text = "Bullish" if macd > macd_signal else "Bearish"
    if macd > macd_signal:
        confidence += 1

    # --- RSI ---
    if rsi > 70:
        rsi_text = "Overbought"
    elif rsi < 30:
        rsi_text = "Oversold"
    else:
        rsi_text = "Neutral"

    # --- Bollinger ---
    if price >= bb_upper:
        bb_text = "Near Upper Band → Possible Reversal"
    elif price <= bb_lower:
        bb_text = "Near Lower Band → Possible Reversal"
    else:
        bb_text = "In Range"

    # --- Decide Signal ---
    if trend == "Uptrend" and ema20 > ema50 and macd > macd_signal and rsi > 50:
        signal = "BUY"
    elif trend == "Downtrend" and ema20 < ema50 and macd < macd_signal and rsi < 50:
        signal = "SELL"
    else:
        signal = "WAIT"

    # --- Risk Management ---
    sl = price - 1.5 * atr if signal == "BUY" else price + 1.5 * atr
    tp = price + 3 * atr if signal == "BUY" else price - 3 * atr

    return {
        "Signal": signal,
        "Confidence": f"{confidence}/5",
        "Trend": trend,
        "EMA Signal": ema_signal,
        "MACD": macd_signal_text,
        "RSI": f"{rsi:.2f} ({rsi_text})",
        "Bollinger": bb_text,
        "Suggested SL": round(sl, 5),
        "Suggested TP": round(tp, 5)
    }
