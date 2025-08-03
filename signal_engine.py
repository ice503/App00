def generate_signal(df, params):
    # Extract last row values as floats
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

    # Strategy params
    rsi_buy = params.get("rsi_buy_threshold", 50)
    rsi_sell = params.get("rsi_sell_threshold", 50)
    atr_mult = params.get("atr_multiplier", 1.5)

    # Determine signal
    trend = "Uptrend" if price > ema200 else "Downtrend"
    confidence = 0
    confidence += 1  # base for trend

    ema_signal = "Bullish" if ema20 > ema50 else "Bearish"
    if ema20 > ema50:
        confidence += 1

    macd_signal_text = "Bullish" if macd > macd_signal else "Bearish"
    if macd > macd_signal:
        confidence += 1

    if rsi > 70:
        rsi_text = "Overbought"
    elif rsi < 30:
        rsi_text = "Oversold"
    else:
        rsi_text = "Neutral"

    if price >= bb_upper:
        bb_text = "Near Upper Band → Possible Reversal"
    elif price <= bb_lower:
        bb_text = "Near Lower Band → Possible Reversal"
    else:
        bb_text = "In Range"

    signal = "WAIT"
    if trend == "Uptrend" and ema20 > ema50 and macd > macd_signal and rsi > rsi_buy:
        signal = "BUY"
    elif trend == "Downtrend" and ema20 < ema50 and macd < macd_signal and rsi < rsi_sell:
        signal = "SELL"

    sl = price - atr_mult * atr if signal == "BUY" else price + atr_mult * atr
    tp = price + 2 * atr_mult * atr if signal == "BUY" else price - 2 * atr_mult * atr

    return {
        "Signal": signal,
        "Confidence": f"{confidence}/5",
        "Trend": trend,
        "EMA Signal": ema_signal,
        "MACD": macd_signal_text,
        "RSI": f"{rsi:.2f} ({rsi_text})",
        "Bollinger": bb_text,
        "Suggested SL": round(sl, 5),
        "Suggested TP": round(tp, 5),
        "ATR Multiplier": atr_mult
    }
