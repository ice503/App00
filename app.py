import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# --- App Title ---
st.set_page_config(layout="wide")
st.title("📈 Forex Trading Signals")
st.write("Basic signal generator using moving averages")

# --- Generate Fake Data ---
@st.cache_data
def load_data():
    np.random.seed(42)
    dates = pd.date_range(end=datetime.today(), periods=100)
    prices = np.cumsum(np.random.randn(100) * 0.01 + 1.0)
    df = pd.DataFrame({"Date": dates, "EUR/USD": prices})
    df["High"] = df["EUR/USD"] + 0.002
    df["Low"] = df["EUR/USD"] - 0.002
    return df

df = load_data()

# --- Calculate Indicators (Pure Python) ---
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

df["MA_Short"] = calculate_sma(df["EUR/USD"], 10)
df["MA_Long"] = calculate_sma(df["EUR/USD"], 50)
df["RSI"] = calculate_rsi(df["EUR/USD"])

# --- Generate Signals ---
df["Signal"] = 0
df.loc[(df["RSI"] < 30) & (df["MA_Short"] > df["MA_Long"]), "Signal"] = 1  # Buy
df.loc[(df["RSI"] > 70) & (df["MA_Short"] < df["MA_Long"]), "Signal"] = -1  # Sell

# --- Simple Risk Management ---
df["Stop_Loss"] = df["EUR/USD"] * 0.995
df["Take_Profit"] = df["EUR/USD"] * 1.005

# --- UI ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔔 Latest Signal")
    latest = df.iloc[-1]
    signal = "🟢 BUY" if latest["Signal"] == 1 else "🔴 SELL" if latest["Signal"] == -1 else "⚪ HOLD"
    st.metric("EUR/USD", f"{latest['EUR/USD']:.5f}", delta=signal)
    st.write(f"Stop Loss: {latest['Stop_Loss']:.5f}")
    st.write(f"Take Profit: {latest['Take_Profit']:.5f}")

with col2:
    st.subheader("📊 Price Chart")
    st.line_chart(df.set_index("Date")["EUR/USD"])

st.subheader("📜 Signal History")
st.dataframe(df.tail(10)[["Date", "EUR/USD", "Signal", "Stop_Loss", "Take_Profit"]])
