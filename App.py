import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from signal_engine import calculate_indicators, generate_signal

st.set_page_config(page_title="📊 Professional Trading Signal Dashboard", layout="wide")

st.title("📊 Professional Trading Signal Dashboard")

# Sidebar for settings
st.sidebar.header("Settings")
symbol = st.sidebar.selectbox(
    "Choose Currency Pair",
    ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "XAUUSD=X", "BTC-USD"],
    index=0
)
interval = st.sidebar.selectbox("Time Interval", ["1h", "30m", "15m", "1d"], index=0)
lookback = st.sidebar.slider("Candles to load", min_value=100, max_value=1000, value=500, step=50)
rr_ratio = st.sidebar.slider("Risk/Reward Ratio", min_value=1.0, max_value=5.0, value=2.0, step=0.5)
atr_multiplier = st.sidebar.slider("ATR Multiplier for Stop Loss", 0.5, 5.0, 1.5, 0.1)

# Determine period for Yahoo Finance
intraday_intervals = ["1m","2m","5m","15m","30m","60m","90m","1h"]
period = "60d" if interval in intraday_intervals else "2y"

# Fetch data
try:
    data = yf.download(tickers=symbol, period=period, interval=interval)
    data.dropna(inplace=True)

    # Fallback: if no data retrieved
    if data.empty:
        st.warning("⚠ No data retrieved with selected interval. Switching to 1d interval.")
        interval = "1d"
        period = "2y"
        data = yf.download(tickers=symbol, period=period, interval=interval)
        data.dropna(inplace=True)

    if data.empty:
        st.error("❌ Still no data retrieved. Try another symbol or interval.")
        st.stop()

    # Keep only the last N rows for display
    data = data.tail(lookback)

    # Calculate indicators and signals
    df = calculate_indicators(data)
    signal_info = generate_signal(df, rr_ratio=rr_ratio, atr_multiplier=atr_multiplier)

    # Candlestick chart with Plotly
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        name="Candlestick"
    ))

    # Add EMAs
    if "EMA20" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["EMA20"], line=dict(color="blue", width=1), name="EMA20"))
    if "EMA50" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["EMA50"], line=dict(color="orange", width=1), name="EMA50"))
    if "EMA200" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["EMA200"], line=dict(color="purple", width=1), name="EMA200"))

    fig.update_layout(
        title=f"📈 Live Chart: {symbol} ({interval})",
        xaxis_rangeslider_visible=False,
        xaxis=dict(type='category'),
        template="plotly_dark",
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)

    # Show last signal
    st.subheader("📢 Latest Signal")
    st.write(signal_info)

except Exception as e:
    st.error(f"Error fetching or processing data: {str(e)}")
