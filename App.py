import streamlit as st
import pandas as pd
import yfinance as yf
import datetime

from signal_engine import calculate_indicators, generate_signal

# ------------------ Streamlit UI ------------------
st.set_page_config(page_title="Pro Forex Signal Dashboard", layout="wide")
st.title("📊 Professional Trading Signal Dashboard")

# Currency pair selection
pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "USD/CHF", "NZD/USD"]
pair = st.selectbox("Select Currency Pair", pairs)

# Interval selection
intervals = ["1m", "5m", "15m", "1h", "4h", "1d"]
interval = st.selectbox("Select Timeframe", intervals)

# Trading parameters
st.sidebar.header("⚙ Strategy Settings")
rr_ratio = st.sidebar.slider("Risk/Reward Ratio", 1.0, 5.0, 2.0)
atr_multiplier = st.sidebar.slider("ATR Multiplier for Stop-Loss", 1.0, 3.0, 1.5)

# ------------------ Fetch Data ------------------
symbol_map = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPY=X",
    "AUD/USD": "AUDUSD=X",
    "USD/CAD": "CAD=X",
    "USD/CHF": "CHF=X",
    "NZD/USD": "NZDUSD=X"
}

data = yf.download(
    symbol_map[pair],
    period="7d",          # Last 7 days
    interval=interval
)

if data.empty:
    st.error("⚠ Failed to fetch data. Try another pair or interval.")
    st.stop()

# Ensure required columns exist
data = data.rename(columns={"Open":"Open","High":"High","Low":"Low","Close":"Close","Volume":"Volume"})

# ------------------ Calculate Indicators & Signal ------------------
try:
    df = calculate_indicators(data)
    signal_info = generate_signal(df, rr_ratio=rr_ratio, atr_multiplier=atr_multiplier)
except Exception as e:
    st.error(f"Error calculating indicators: {e}")
    st.stop()

# ------------------ Display Signal ------------------
st.subheader("📢 Trading Signal")
if signal_info:
    st.success(f"**Signal:** {signal_info['signal']} | "
               f"Entry: {signal_info['entry']:.5f} | "
               f"SL: {signal_info['stop_loss']:.5f} | "
               f"TP: {signal_info['take_profit']:.5f}")
else:
    st.info("No clear signal detected based on the current strategy.")

# ------------------ TradingView Chart Embed ------------------
st.subheader(f"📈 Live Chart: {pair} ({interval})")

interval_map_tv = {
    "1m": "1",
    "5m": "5",
    "15m": "15",
    "1h": "60",
    "4h": "240",
    "1d": "D"
}

symbol_map_tv = {
    "EUR/USD": "FX:EURUSD",
    "GBP/USD": "FX:GBPUSD",
    "USD/JPY": "FX:USDJPY",
    "AUD/USD": "FX:AUDUSD",
    "USD/CAD": "FX:USDCAD",
    "USD/CHF": "FX:USDCHF",
    "NZD/USD": "FX:NZDUSD"
}

embed_code = f"""
<iframe src="https://s.tradingview.com/widgetembed/?symbol={symbol_map_tv[pair]}&interval={interval_map_tv[interval]}&theme=dark&style=1&locale=en&toolbarbg=f1f3f6&enable_publishing=false&withdateranges=true&allow_symbol_change=true&save_image=false&studies=[]" 
width="100%" height="600" frameborder="0" allowfullscreen></iframe>
"""
st.markdown(embed_code, unsafe_allow_html=True)
