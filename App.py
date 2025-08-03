import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="EUR/USD Analyzer", layout="wide")
st.title("📊 EUR/USD 1-Hour Analyzer & Strategy Suggestion")

# --- Fetch last 7 days of 1-hour data ---
end = datetime.now()
start = end - timedelta(days=7)
data = yf.download("EURUSD=X", interval="1h", start=start, end=end)

# --- Check if data is empty ---
if data.empty:
    st.error("⚠ No data fetched from Yahoo Finance. Try again later or use a VPN.")
else:
    # --- Calculate Indicators ---
    data['RSI'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
    data['MA50'] = data['Close'].rolling(50).mean()

    # --- Plot Candlestick Chart with MA50 ---
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Price"
    )])
    fig.add_trace(go.Scatter(
        x=data.index, y=data['MA50'],
        line=dict(color='blue', width=1.5),
        name='MA50'
    ))
    fig.update_layout(xaxis_rangeslider_visible=False, height=600)
    st.plotly_chart(fig, use_container_width=True)

    # --- Strategy Suggestion ---
    last_close = data['Close'].iloc[-1]
    last_rsi = data['RSI'].iloc[-1]
    last_ma50 = data['MA50'].iloc[-1]

    st.subheader("💡 Suggested Strategy:")

    if last_close > last_ma50 and last_rsi > 50:
        st.success("**Market is in uptrend** → Consider a **trend-following strategy** (Buy dips).")
    elif last_rsi < 30:
        st.warning("**Market is oversold** → Potential **bounce/scalping opportunity**.")
    else:
        st.info("**Market is ranging** → Consider **range-trading strategy** (Support/Resistance).")

    # --- Extra Info ---
    st.caption(f"Last Close: {last_close:.5f} | RSI: {last_rsi:.2f} | MA50: {last_ma50:.5f}")
