import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="EUR/USD Analyzer", layout="wide")
st.title("📊 EUR/USD 1-Hour Analyzer & Strategy Suggestion")

# --- Fetch last 7 days of 1-hour data ---
end = datetime.now()
start = end - timedelta(days=7)
data = yf.download("EURUSD=X", interval="1h", start=start, end=end)

# --- Check if data is empty ---
if data.empty or "Close" not in data:
    st.error("⚠ No Forex data fetched. Yahoo Finance may block EUR/USD on cloud servers.")
    st.info("Try again later or switch to a stock/crypto symbol for testing.")
else:
    # --- Ensure Close is 1-dimensional ---
    close_prices = data['Close'].squeeze()

    # --- Calculate RSI manually to avoid TA-Lib 2D errors ---
    def compute_rsi(series, period=14):
        delta = series.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.rolling(window=period, min_periods=period).mean()
        avg_loss = loss.rolling(window=period, min_periods=period).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    data['RSI'] = compute_rsi(close_prices)
    data['MA50'] = close_prices.rolling(50).mean()

    # --- Plot Candlestick Chart ---
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=close_prices,
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
    last_close = close_prices.iloc[-1]
    last_rsi = data['RSI'].iloc[-1]
    last_ma50 = data['MA50'].iloc[-1]

    st.subheader("💡 Suggested Strategy:")

    if last_close > last_ma50 and last_rsi > 50:
        st.success("**Uptrend** → Consider **trend-following strategy** (Buy dips).")
    elif last_rsi < 30:
        st.warning("**Oversold** → Potential **bounce/scalping opportunity**.")
    else:
        st.info("**Ranging market** → Consider **range-trading strategy** (Support/Resistance).")

    st.caption(f"Last Close: {last_close:.5f} | RSI: {last_rsi:.2f} | MA50: {last_ma50:.5f}")
