import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

# --- Shared Strategy Logic ---
def calculate_rsi(series, window=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def generate_signals(df, price_col='Price'):
    df = df.copy()
    df["MA10"] = df[price_col].rolling(10).mean()
    df["MA50"] = df[price_col].rolling(50).mean()
    df["RSI"] = calculate_rsi(df[price_col])
    
    df["Signal"] = 0
    df.loc[(df["RSI"] < 30) & (df["MA10"] > df["MA50"]), "Signal"] = 1  # Buy
    df.loc[(df["RSI"] > 70) & (df["MA10"] < df["MA50"]), "Signal"] = -1  # Sell
    return df

# --- Live Signal Generator (Compatible with your original data) ---
def live_signal_app():
    st.header("📈 Live Signal Generator")
    pair = st.selectbox("Currency Pair", ["EUR/USD", "GBP/USD", "USD/JPY"], key='live_pair')
    
    # Simulate your original data structure
    dates = pd.date_range(end=datetime.now(), periods=100)
    prices = {
        "EUR/USD": 1.08 + np.cumsum(np.random.randn(100) * 0.002),
        "GBP/USD": 1.26 + np.cumsum(np.random.randn(100) * 0.002),
        "USD/JPY": 151.50 + np.cumsum(np.random.randn(100) * 0.2)
    }[pair]
    
    data = pd.DataFrame({
        "Date": dates,
        "Price": prices,
        "High": prices + 0.0015,
        "Low": prices - 0.0015
    })
    
    signals = generate_signals(data)
    latest = signals.iloc[-1]
    
    st.metric(
        label=pair,
        value=f"{latest['Price']:.5f}",
        delta="BUY 🟢" if latest['Signal'] == 1 else "SELL 🔴" if latest['Signal'] == -1 else "HOLD ⚪"
    )
    st.line_chart(signals.set_index('Date')[['Price', 'MA10', 'MA50']])

# --- Backtester (Using Yahoo Finance) ---
def backtester_app():
    st.header("🔍 Strategy Backtester")
    
    col1, col2 = st.columns(2)
    with col1:
        pair = st.selectbox("Pair", ["EURUSD=X", "GBPUSD=X", "USDJPY=X"], key='backtest_pair')
    with col2:
        years = st.slider("Test Period (Years)", 1, 5, 2, key='years')
    
    if st.button("Run Backtest"):
        data = yf.download(pair, period=f"{years}y")
        if not data.empty:
            signals = generate_signals(data, price_col='Close')
            latest = signals.iloc[-1]
            
            st.metric(
                label=pair,
                value=f"{latest['Close']:.5f}",
                delta="BUY 🟢" if latest['Signal'] == 1 else "SELL 🔴" if latest['Signal'] == -1 else "HOLD ⚪"
            )
            st.line_chart(signals[['Close', 'MA10', 'MA50']])
        else:
            st.error("Failed to fetch historical data")

# --- Main App ---
st.set_page_config(layout="wide")
st.title("Forex Trading Toolkit")

tab1, tab2 = st.tabs(["Live Signals", "Backtester"])
with tab1:
    live_signal_app()
with tab2:
    backtester_app()
