import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- Page setup ---
st.set_page_config(page_title="EUR/USD Strategy Tester", layout="wide")
st.title("🤖 EUR/USD 1-Hour Strategy Tester & Recommendation")

# --- Step 1: Fetch last 7 days of EUR/USD ---
end = datetime.now()
start = end - timedelta(days=7)
data = yf.download("EURUSD=X", interval="1h", start=start, end=end)

if data.empty:
    st.error("⚠ No data fetched. Yahoo Finance may block Forex on cloud servers.")
else:
    # --- Step 2: Compute indicators ---
    # Moving Averages
    data['MA20'] = data['Close'].rolling(20).mean()
    data['MA50'] = data['Close'].rolling(50).mean()

    # RSI 14
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = data['Close'].ewm(span=12, adjust=False).mean()
    ema26 = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = ema12 - ema26
    data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()

    # Bollinger Bands
    data['BB_Mid'] = data['Close'].rolling(20).mean()
    data['BB_Upper'] = data['BB_Mid'] + 2*data['Close'].rolling(20).std()
    data['BB_Lower'] = data['BB_Mid'] - 2*data['Close'].rolling(20).std()

    # --- Step 3: Show candlestick chart with MA50 ---
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Price"
    )])
    fig.add_trace(go.Scatter(x=data.index, y=data['MA50'], line=dict(color='blue', width=1.5), name='MA50'))
    fig.add_trace(go.Scatter(x=data.index, y=data['BB_Upper'], line=dict(color='green', width=1), name='BB Upper'))
    fig.add_trace(go.Scatter(x=data.index, y=data['BB_Lower'], line=dict(color='red', width=1), name='BB Lower'))
    fig.update_layout(xaxis_rangeslider_visible=False, height=600)
    st.plotly_chart(fig, use_container_width=True)

    # --- Step 4: Determine last signal of each indicator ---
    last_close = float(data['Close'].iloc[-1])
    last_rsi = float(data['RSI'].iloc[-1])
    last_ma20 = float(data['MA20'].iloc[-1])
    last_ma50 = float(data['MA50'].iloc[-1])
    last_macd = float(data['MACD'].iloc[-1])
    last_signal = float(data['Signal'].iloc[-1])

    signals = []

    # Trend (Moving Average Crossover)
    if last_ma20 > last_ma50:
        signals.append("Trend-Following (Uptrend)")
    else:
        signals.append("Trend-Following (Downtrend)")

    # RSI
    if last_rsi > 70:
        signals.append("RSI Overbought → Consider selling or waiting for pullback")
    elif last_rsi < 30:
        signals.append("RSI Oversold → Consider buying or waiting for bounce")

    # MACD
    if last_macd > last_signal:
        signals.append("MACD Bullish → Momentum up")
    else:
        signals.append("MACD Bearish → Momentum down")

    # Bollinger Bands
    if last_close >= data['BB_Upper'].iloc[-1]:
        signals.append("Price at Upper Band → Potential Reversal Down")
    elif last_close <= data['BB_Lower'].iloc[-1]:
        signals.append("Price at Lower Band → Potential Reversal Up")

    # --- Step 5: Suggest the most accurate strategy based on last week ---
    st.subheader("📊 Strategy Recommendation")
    if last_ma20 > last_ma50 and last_macd > last_signal and last_rsi > 50:
        st.success("Best Strategy: **Trend-Following / Buy Dips** (Strong Uptrend)")
    elif last_rsi < 30 or last_close <= data['BB_Lower'].iloc[-1]:
        st.warning("Best Strategy: **Scalping / Bounce Trading** (Market Oversold)")
    else:
        st.info("Best Strategy: **Range-Trading** (Sideways or Mixed Signals)")

    # --- Step 6: Show all indicator signals ---
    st.write("### 🔍 Indicator Signals")
    for s in signals:
        st.write("- " + s)
