import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- Page setup ---
st.set_page_config(page_title="EUR/USD Analyzer", layout="wide")
st.title("📊 EUR/USD 1-Hour Analyzer & Strategy Suggestion")

# --- Step 1: Get the past 7 days of EUR/USD (1-hour) ---
end = datetime.now()
start = end - timedelta(days=7)

data = yf.download("EURUSD=X", interval="1h", start=start, end=end)

# --- Step 2: Check if we got data ---
if data.empty:
    st.error("⚠ No data fetched. Yahoo Finance sometimes blocks Forex on cloud servers.")
else:
    # --- Step 3: Calculate simple indicators manually ---
    # Moving Average 50 (trend line)
    data['MA50'] = data['Close'].rolling(50).mean()

    # RSI 14 (overbought/oversold)
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))

    # --- Step 4: Show chart ---
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

    # --- Step 5: Suggest a simple strategy ---
    last_close = float(data['Close'].iloc[-1])
    last_rsi = float(data['RSI'].iloc[-1])
    last_ma50 = float(data['MA50'].iloc[-1])

    st.subheader("💡 Suggested Strategy:")

    if last_close > last_ma50 and last_rsi > 50:
        st.success("**Uptrend** → Consider **trend-following (buy dips)**")
    elif last_rsi < 30:
        st.warning("**Oversold** → Possible **bounce/scalping** opportunity")
    else:
        st.info("**Sideways market** → Consider **range-trading (support/resistance)**")

    st.caption(f"Last Close: {last_close:.5f} | RSI: {last_rsi:.2f} | MA50: {last_ma50:.5f}")
