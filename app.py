import streamlit as st
import pandas as pd
import numpy as np
import pandas_ta as ta
from datetime import datetime

# --- App Title ---
st.set_page_config(layout="wide")
st.title("📈 Forex Trading Signals")
st.write("Generates BUY/SELL signals using RSI & Moving Averages")

# --- Generate Fake Data (Replace with API later) ---
@st.cache_data
def load_data():
    dates = pd.date_range(end=datetime.today(), periods=100).tolist()
    prices = np.cumsum(np.random.randn(100) * 0.01 + 1.0)  # Fake EUR/USD prices
    df = pd.DataFrame({"Date": dates, "EUR/USD": prices})
    
    # Generate High/Low/Close (needed for ATR)
    df["High"] = df["EUR/USD"] + 0.002
    df["Low"] = df["EUR/USD"] - 0.002
    df["Close"] = df["EUR/USD"]
    return df

df = load_data()

# --- Calculate Indicators ---
def generate_signals(df):
    # RSI and Moving Averages
    df["RSI"] = ta.rsi(df["Close"], length=14)
    df["MA_Short"] = ta.sma(df["Close"], length=10)
    df["MA_Long"] = ta.sma(df["Close"], length=50)
    
    # Generate signals (1=Buy, -1=Sell, 0=Hold)
    df["Signal"] = 0
    df.loc[(df["RSI"] < 30) & (df["MA_Short"] > df["MA_Long"]), "Signal"] = 1  # Buy
    df.loc[(df["RSI"] > 70) & (df["MA_Short"] < df["MA_Long"]), "Signal"] = -1  # Sell
    
    # Stop Loss & Take Profit (1.5x ATR)
    atr = ta.atr(df["High"], df["Low"], df["Close"], length=14)
    df["Stop_Loss"] = np.where(df["Signal"] == 1, df["Close"] - 1.5 * atr, df["Close"] + 1.5 * atr)
    df["Take_Profit"] = np.where(df["Signal"] == 1, df["Close"] + 2 * atr, df["Close"] - 2 * atr)
    
    return df

df = generate_signals(df)

# --- UI Layout ---
col1, col2 = st.columns([1, 2])

with col1:
    # --- Latest Signal ---
    st.subheader("🔔 Latest Signal")
    latest = df.iloc[-1]
    signal_emoji = "🟢 BUY" if latest["Signal"] == 1 else "🔴 SELL" if latest["Signal"] == -1 else "⚪ HOLD"
    
    st.metric("EUR/USD", f"{latest['Close']:.5f}", delta=signal_emoji)
    st.write(f"**Stop Loss:** {latest['Stop_Loss']:.5f}")
    st.write(f"**Take Profit:** {latest['Take_Profit']:.5f}")

with col2:
    # --- Price Chart ---
    st.subheader("📊 Price with Signals")
    st.line_chart(df.set_index("Date")["Close"])

# --- Signal History ---
st.subheader("📜 Last 10 Signals")
history_cols = ["Date", "Close", "Signal", "Stop_Loss", "Take_Profit"]
st.dataframe(df[history_cols].tail(10).style.applymap(
    lambda x: "background-color: #d4edda" if x == 1 else "background-color: #f8d7da" if x == -1 else ""
))

# --- Accuracy Metrics (Placeholder) ---
st.subheader("🎯 Performance Metrics")
st.progress(75)
st.write("**Win Rate:** 75% (Placeholder - Connect to real data)")
