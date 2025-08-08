import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# --- App Config ---
st.set_page_config(layout="wide")
st.title("💱 Multi-Currency Forex Signals")
st.write("Real-time trading signals for major currency pairs")

# --- Available Forex Pairs ---
FOREX_PAIRS = {
    "EUR/USD": "Euro vs US Dollar",
    "GBP/USD": "British Pound vs US Dollar",
    "USD/JPY": "US Dollar vs Japanese Yen",
    "AUD/USD": "Australian Dollar vs US Dollar",
    "USD/CAD": "US Dollar vs Canadian Dollar"
}

# --- Generate Fake Data for All Pairs ---
@st.cache_data
def generate_forex_data():
    np.random.seed(42)
    dates = pd.date_range(end=datetime.today(), periods=100)
    data = {}
    
    for pair in FOREX_PAIRS:
        # Generate realistic price ranges for each pair
        base_price = {
            "EUR/USD": 1.08,
            "GBP/USD": 1.26,
            "USD/JPY": 151.50,
            "AUD/USD": 0.66,
            "USD/CAD": 1.36
        }[pair]
        
        # FIXED: Added missing parenthesis here
        prices = base_price + np.cumsum(np.random.randn(100) * 0.005
        data[pair] = pd.DataFrame({
            "Date": dates,
            "Price": prices,
            "High": prices + 0.002,
            "Low": prices - 0.002
        })
    return data

# --- Technical Indicators (Pure Python) ---
def calculate_sma(series, window):
    return series.rolling(window=window).mean()

def calculate_rsi(series, window=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# --- Generate Signals for All Pairs ---
def generate_signals(forex_data):
    signals = {}
    for pair, df in forex_data.items():
        df = df.copy()
        df["MA_Short"] = calculate_sma(df["Price"], 10)
        df["MA_Long"] = calculate_sma(df["Price"], 50)
        df["RSI"] = calculate_rsi(df["Price"])
        
        df["Signal"] = 0
        df.loc[(df["RSI"] < 30) & (df["MA_Short"] > df["MA_Long"]), "Signal"] = 1
        df.loc[(df["RSI"] > 70) & (df["MA_Short"] < df["MA_Long"]), "Signal"] = -1
        
        # Dynamic stop levels (1.5% risk)
        df["Stop_Loss"] = np.where(
            df["Signal"] == 1,
            df["Price"] * 0.985,
            df["Price"] * 1.015
        )
        df["Take_Profit"] = np.where(
            df["Signal"] == 1,
            df["Price"] * 1.02,
            df["Price"] * 0.98
        )
        signals[pair] = df
    return signals

# --- UI Components ---
def display_pair_signals(pair, df):
    latest = df.iloc[-1]
    signal_emoji = "🟢 BUY" if latest["Signal"] == 1 else "🔴 SELL" if latest["Signal"] == -1 else "⚪ HOLD"
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric(pair, f"{latest['Price']:.5f}", delta=signal_emoji)
        st.caption(f"SL: {latest['Stop_Loss']:.5f}")
        st.caption(f"TP: {latest['Take_Profit']:.5f}")
    with col2:
        st.line_chart(df.set_index("Date")["Price"])

# --- Main App ---
forex_data = generate_forex_data()
signals = generate_signals(forex_data)

selected_pair = st.selectbox(
    "Select Currency Pair", 
    list(FOREX_PAIRS.keys()), 
    format_func=lambda x: f"{x} ({FOREX_PAIRS[x]})"
)

st.header(f"{selected_pair} Analysis")
display_pair_signals(selected_pair, signals[selected_pair])

st.header("📊 All Pair Signals")
for pair in FOREX_PAIRS:
    expander = st.expander(f"{pair} Summary")
    with expander:
        display_pair_signals(pair, signals[pair])

st.header("📜 Signal History")
st.dataframe(
    pd.concat({
        pair: df.tail(3)[["Date", "Price", "Signal", "Stop_Loss", "Take_Profit"]]
        for pair, df in signals.items()
    }),
    height=500
)
