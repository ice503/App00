import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# --- App Config ---
st.set_page_config(layout="wide")
st.title("💱 Forex Trading Signals")
st.write("Simple multi-currency signal generator")

# --- Forex Pairs ---
PAIRS = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD"]
BASE_PRICES = {
    "EUR/USD": 1.08,
    "GBP/USD": 1.26,
    "USD/JPY": 151.50,
    "AUD/USD": 0.66,
    "USD/CAD": 1.36
}

# --- Data Generation (Simplified) ---
@st.cache_data
def generate_data():
    dates = pd.date_range(end=datetime.today(), periods=100)
    data = {}
    
    for pair in PAIRS:
        # Simplified price generation
        random_values = np.random.randn(100) * 0.005
        cumulative = np.cumsum(random_values)
        prices = BASE_PRICES[pair] + cumulative
        
        df = pd.DataFrame({
            "Date": dates,
            "Price": prices,
            "High": prices + 0.002,
            "Low": prices - 0.002
        })
        data[pair] = df
    return data

# --- Technical Indicators ---
def sma(series, window):
    return series.rolling(window).mean()

def rsi(series, window=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# --- Signal Generation ---
def generate_signals(data):
    signals = {}
    for pair, df in data.items():
        df = df.copy()
        df["MA10"] = sma(df["Price"], 10)
        df["MA50"] = sma(df["Price"], 50)
        df["RSI"] = rsi(df["Price"])
        
        df["Signal"] = 0
        df.loc[(df["RSI"] < 30) & (df["MA10"] > df["MA50"]), "Signal"] = 1
        df.loc[(df["RSI"] > 70) & (df["MA10"] < df["MA50"]), "Signal"] = -1
        
        df["Stop_Loss"] = df["Price"] * 0.985
        df["Take_Profit"] = df["Price"] * 1.015
        
        signals[pair] = df
    return signals

# --- UI Display ---
def show_pair(pair, df):
    latest = df.iloc[-1]
    signal = "BUY 🟢" if latest["Signal"] == 1 else "SELL 🔴" if latest["Signal"] == -1 else "HOLD ⚪"
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric(pair, f"{latest['Price']:.5f}", signal)
        st.write(f"SL: {latest['Stop_Loss']:.5f}")
        st.write(f"TP: {latest['Take_Profit']:.5f}")
    with col2:
        st.line_chart(df.set_index("Date")["Price"])

# --- Main App ---
data = generate_data()
signals = generate_signals(data)

pair = st.selectbox("Select Pair", PAIRS)
st.header(f"{pair} Analysis")
show_pair(pair, signals[pair])

st.header("All Signals")
for p in PAIRS:
    with st.expander(p):
        show_pair(p, signals[p])
