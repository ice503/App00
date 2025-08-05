import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from signal_engine import calculate_indicators, generate_signal

st.set_page_config(layout="wide", page_title="📊 Professional Trading Signal Dashboard")

st.title("📊 Professional Trading Signal Dashboard")

# Sidebar
st.sidebar.header("Settings")
pair = st.sidebar.selectbox("Select Currency Pair", ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X"])
timeframe = st.sidebar.selectbox("Select Timeframe", ["1h", "30m", "15m"])
period = st.sidebar.selectbox("Select Data Period", ["5d", "1mo", "3mo"])

st.sidebar.markdown("Adjust Risk Management")
rr_ratio = st.sidebar.slider("Risk-Reward Ratio", 1.0, 3.0, 2.0)
atr_multiplier = st.sidebar.slider("ATR Multiplier for Stop Loss", 1.0, 3.0, 1.5)

# Load data
try:
    data = yf.download(pair, period=period, interval=timeframe)
    data = data.reset_index()  # Reset index for plotting
    data.rename(columns={"Open":"Open","High":"High","Low":"Low","Close":"Close"}, inplace=True)

    if data.empty:
        st.warning("No data found for this selection.")
    else:
        df = calculate_indicators(data)
        signal_info = generate_signal(df, rr_ratio=rr_ratio, atr_multiplier=atr_multiplier)

        st.subheader("Latest Signal")
        st.write(signal_info)

        # Candlestick Chart
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df['Datetime'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Candlestick'
        ))
        fig.update_layout(
            title=f"Live Candlestick Chart: {pair} ({timeframe})",
            xaxis_rangeslider_visible=False,
            template="plotly_dark",
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error: {str(e)}")
