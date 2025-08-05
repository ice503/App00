import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from signal_engine import calculate_indicators, generate_signal
from streamlit_tradingview_chart import tradingview_chart

# ---------------------------
# Streamlit Page Config
# ---------------------------
st.set_page_config(page_title="Pro Trading Signals", layout="wide")
st.title("📊 Professional Trading Signal Dashboard")

# ---------------------------
# Sidebar Settings
# ---------------------------
st.sidebar.header("⚙ Settings")

pairs = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPY=X",
    "AUD/USD": "AUDUSD=X",
    "USD/CAD": "CAD=X",
    "USD/CHF": "CHF=X",
    "NZD/USD": "NZDUSD=X"
}
pair = st.sidebar.selectbox("Select Currency Pair", list(pairs.keys()))
symbol = pairs[pair]

interval = st.sidebar.selectbox(
    "Timeframe", ["1m", "5m", "15m", "1h", "4h", "1d"], index=3
)

lookback_days = st.sidebar.slider("Historical Days", 7, 90, 30)
rr_ratio = st.sidebar.slider("Risk-Reward Ratio", 1.0, 5.0, 2.0)
atr_multiplier = st.sidebar.slider("ATR Multiplier (Stop Loss)", 1.0, 3.0, 1.5)

# ---------------------------
# Fetch Historical Data
# ---------------------------
interval_map = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "1h": "1h",
    "4h": "4h",
    "1d": "1d"
}

data = yf.download(
    symbol,
    period=f"{lookback_days}d",
    interval=interval_map[interval]
)

if data.empty:
    st.error("⚠ Could not fetch data. Try a different pair or timeframe.")
    st.stop()

# Reset index to get Open/High/Low/Close properly
data.reset_index(inplace=True)
data.rename(columns={"Open":"Open", "High":"High", "Low":"Low", "Close":"Close"}, inplace=True)

# ---------------------------
# Calculate Indicators
# ---------------------------
df = calculate_indicators(data)

# ---------------------------
# Generate Signal
# ---------------------------
signal_info = generate_signal(df, rr_ratio=rr_ratio, atr_multiplier=atr_multiplier)

# Display current signal
st.subheader(f"🎯 Trading Signal for {pair}")
if signal_info["signal"] != "HOLD":
    st.success(
        f"{signal_info['signal']} | SL: {signal_info['stop_loss']} | TP: {signal_info['take_profit']}"
    )
else:
    st.info("No clear signal. Waiting for confluence.")

# ---------------------------
# TradingView-Like Chart
# ---------------------------
st.subheader(f"📈 {pair} Live Chart (TradingView Style)")

interval_map_tv = {
    "1m": "1",
    "5m": "5",
    "15m": "15",
    "1h": "60",
    "4h": "240",
    "1d": "D"
}

tradingview_chart(
    symbol=symbol,
    interval=interval_map_tv[interval],
    theme="dark",
    timezone="Etc/UTC",
    style="1",          # 1 = candlesticks
    autosize=True,
    enable_publishing=False,
    hide_top_toolbar=False,
    hide_legend=False,
    save_image=False
)

st.caption("💡 Zoom, pan, and fullscreen supported like TradingView.")
