import streamlit as st
import pandas as pd
import numpy as np
import talib
from datetime import datetime

# --- App Title ---
st.title("📈 Forex Trading Signals")
st.write("Generates BUY/SELL signals using RSI & Moving Averages")

# --- Fake Data (Replace with real Forex API later) ---
def load_data():
    dates = pd.date_range(end=datetime.today(), periods=100).tolist()
    prices = np.cumsum(np.random.randn(100) * 0.01 + 1.0)  # Fake EUR/USD prices
    return pd.DataFrame({"Date": dates, "EUR/USD": prices})

df = load_data()

# --- Calculate Indicators ---
def generate_signals(df):
    close_prices = df["EUR/USD"].values
    df["RSI"] = talib.RSI(close_prices, timeperiod=14)
    df["MA_Short"] = talib.SMA(close_prices, timeperiod=10)
    df["MA_Long"] = talib.SMA(close_prices, timeperiod=50)
    
    # Generate signals (1=Buy, -1=Sell, 0=Hold)
    df["Signal"] = 0
    df.loc[(df["RSI"] < 30) & (df["MA_Short"] > df["MA_Long"]), "Signal"] = 1  # Buy
    df.loc[(df["RSI"] > 70) & (df["MA_Short"] < df["MA_Long"]), "Signal"] = -1  # Sell
    
    # Stop Loss & Take Profit (1.5x ATR)
    atr = talib.ATR(df["EUR/USD"].shift(1), df["EUR/USD"].shift(1), close_prices, timeperiod=14)
    df["Stop_Loss"] = np.where(df["Signal"] == 1, df["EUR/USD"] - 1.5 * atr, df["EUR/USD"] + 1.5 * atr)
    df["Take_Profit"] = np.where(df["Signal"] == 1, df["EUR/USD"] + 2 * atr, df["EUR/USD"] - 2 * atr)
    
    return df

df = generate_signals(df)

# --- Show Latest Signal ---
latest_signal = df.iloc[-1]
st.subheader("🔔 Latest Signal")
st.write(f"**EUR/USD:** {latest_signal['EUR/USD']:.5f}")
st.write(f"**Signal:** {'BUY 🟢' if latest_signal['Signal'] == 1 else 'SELL 🔴' if latest_signal['Signal'] == -1 else 'HOLD ⚪'}")
st.write(f"**Stop Loss:** {latest_signal['Stop_Loss']:.5f}")
st.write(f"**Take Profit:** {latest_signal['Take_Profit']:.5f}")

# --- Signal History Table ---
st.subheader("📜 Signal History")
st.dataframe(df.tail(10)[["Date", "EUR/USD", "Signal", "Stop_Loss", "Take_Profit"]])

# --- Accuracy Tracking (Fake for now) ---
st.subheader("🎯 Accuracy")
st.write("(Will calculate later based on real price movements)")
