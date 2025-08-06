import streamlit as st
import pandas as pd
from core.signals import generate_signal
from core.risk_manager import calculate_risk_levels
from core.analytics import calculate_performance
from core.multi_timeframe import scan_multi_timeframe

st.set_page_config(page_title="Trading AI Dashboard", layout="wide")

st.sidebar.header("Trading Settings")
symbol = st.sidebar.selectbox("Symbol", ["EURUSD", "GBPUSD", "XAUUSD"])
timeframe = st.sidebar.selectbox("Timeframe", ["M15", "H1", "H4"])
risk_ratio = st.sidebar.slider("Risk/Reward Ratio", 1.0, 5.0, 2.0)

st.title("📊 Trading AI Dashboard")

# Simulated data (replace with live feed later)
df = pd.DataFrame({
    "close": [1.10, 1.105, 1.102, 1.108],
    "high": [1.11, 1.106, 1.104, 1.109],
    "low": [1.09, 1.103, 1.100, 1.107]
})

# Generate Signal
signal = generate_signal(df)
st.subheader(f"Real-Time Signal: {signal}")

# Calculate Risk Levels
entry_price = df["close"].iloc[-1]
sl, tp = calculate_risk_levels(df, entry_price, risk_ratio)
st.write(f"**Entry Price:** {entry_price:.5f}")
st.write(f"**Stop-Loss:** {sl:.5f}")
st.write(f"**Take-Profit:** {tp:.5f}")

# Multi-Timeframe Scan
st.subheader("Multi-Timeframe Convergence")
convergence = scan_multi_timeframe(symbol)
st.write(convergence)

# Performance Analytics (Sample)
st.subheader("Performance Analytics")
metrics = calculate_performance()
st.write(metrics)

st.success("✅ Dashboard loaded successfully!")
