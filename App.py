import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from indicators import calculate_indicators
from signal_engine import generate_signal

# --- Streamlit page setup ---
st.set_page_config(page_title="Pro Forex Signal App", layout="wide")
st.title("📊 Professional Forex Signal & Strategy App")

# --- User Inputs ---
symbol = st.selectbox("Select Pair", ["EURUSD=X", "GBPUSD=X", "BTC-USD"])
timeframe = st.selectbox("Timeframe", ["1h", "4h", "1d"])
days = st.slider("History (days)", 7, 60, 30)

# --- Fetch Data ---
data = yf.download(symbol, period=f"{days}d", interval=timeframe)
if data.empty:
    st.error("⚠ No data fetched. Try again later.")
else:
    # --- Compute indicators ---
    df = calculate_indicators(data)
    
    # --- Plot candlestick with EMAs ---
    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']
    )])
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='blue'), name='EMA20'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], line=dict(color='orange'), name='EMA50'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], line=dict(color='red'), name='EMA200'))
    st.plotly_chart(fig, use_container_width=True)

    # --- Show latest signal ---
    st.subheader("📈 Latest Signal Recommendation")
    signal_info = generate_signal(df)
    st.write(signal_info)
