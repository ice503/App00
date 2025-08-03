def generate_signal(df):
    # --- Extract last row values as floats ---
    price = float(df['Close'].iloc[-1])
    ema20 = float(df['EMA20'].iloc[-1])
    ema50 = float(df['EMA50'].iloc[-1])
    ema200 = float(df['EMA200'].iloc[-1])
    macd = float(df['MACD'].iloc[-1])
    macd_signal = float(df['MACD_Signal'].iloc[-1])
    rsi = float(df['RSI'].iloc[-1])
    atr = float(df['ATR'].iloc[-1])
    bb_upper = float(df['BB_Upper'].iloc[-1])
    bb_lower = float(df['BB_Lower'].iloc[-1])

    # --- Initialize variables ---
    confidence = 0
    trend = ""
    ema_signal = ""
    macd_signal_text = ""
    rsi_text = ""
    bb_text = ""
    signal = "WAIT"

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

    # --- Bollinger Bands ---
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

    # --- Return as dictionary ---
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
