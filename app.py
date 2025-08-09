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

def generate_signals(df, price_col='Close'):
    """Universal signal generator that works with any data format"""
    df = df.copy()
    
    # Auto-detect price column if not specified
    if price_col not in df.columns:
        for col in ['Close', 'Price', 'Last', 'price']:
            if col in df.columns:
                price_col = col
                break
        else:  # No matching column found
            price_col = df.columns[0]
    
    # Ensure numeric data
    df[price_col] = pd.to_numeric(df[price_col], errors='coerce')
    df = df.dropna(subset=[price_col])
    
    df["MA10"] = df[price_col].rolling(10).mean()
    df["MA50"] = df[price_col].rolling(50).mean()
    df["RSI"] = calculate_rsi(df[price_col])
    
    df["Signal"] = 0
    df.loc[(df["RSI"] < 30) & (df["MA10"] > df["MA50"]), "Signal"] = 1
    df.loc[(df["RSI"] > 70) & (df["MA10"] < df["MA50"]), "Signal"] = -1
    return df, price_col

# --- Live Signal Generator ---
def live_signal_app():
    st.header("📈 Live Signal Generator")
    pair = st.selectbox("Currency Pair", ["EUR/USD", "GBP/USD", "USD/JPY"], key='live_pair')
    
    # Synthetic data with realistic ranges
    dates = pd.date_range(end=datetime.now(), periods=100)
    prices = {
        "EUR/USD": 1.08 + np.cumsum(np.random.randn(100) * 0.002),
        "GBP/USD": 1.26 + np.cumsum(np.random.randn(100) * 0.002),
        "USD/JPY": 151.50 + np.cumsum(np.random.randn(100) * 0.2)
    }[pair]
    
    data = pd.DataFrame({"Date": dates, "Price": prices})
    signals, price_col = generate_signals(data, 'Price')
    display_signals(pair, signals, price_col)

# --- Backtester ---
def backtester_app():
    st.header("🔍 Strategy Backtester")
    
    col1, col2 = st.columns(2)
    with col1:
        pair = st.selectbox("Pair", ["EURUSD=X", "GBPUSD=X", "USDJPY=X"], key='backtest_pair')
    with col2:
        years = st.slider("Test Period", 1, 5, 2, key='years')
    
    if st.button("Run Backtest"):
        with st.spinner("Fetching historical data..."):
            data = yf.download(pair, period=f"{years}y")
            if not data.empty:
                signals, price_col = generate_signals(data)
                display_signals(pair.replace("=X", ""), signals, price_col)
            else:
                st.error("No data available. Try a different pair or time range.")

# --- Universal Display Function ---
def display_signals(pair, signals, price_col):
    """Robust display that handles any numeric data format"""
    try:
        latest = signals.iloc[-1]
        price_value = float(latest[price_col])
        
        st.metric(
            label=pair,
            value=f"{price_value:.5f}".rstrip('0').rstrip('.') if '.' in f"{price_value:.5f}" else f"{price_value:.5f}",
            delta="BUY 🟢" if latest['Signal'] == 1 else "SELL 🔴" if latest['Signal'] == -1 else "HOLD ⚪"
        )
        
        # Prepare chart data
        chart_data = signals[[price_col, "MA10", "MA50"]].copy()
        chart_data.columns = ["Price", "MA(10)", "MA(50)"]
        st.line_chart(chart_data)
        
        # Show recent signals
        st.subheader("Recent Signals")
        st.dataframe(signals[['Date' if 'Date' in signals.columns else signals.index.name, 
                            price_col, 'Signal']].tail(10))
        
    except Exception as e:
        st.error(f"Display error: {str(e)}")

# --- Main App ---
st.set_page_config(layout="wide")
st.title("Forex Trading Toolkit")

tab1, tab2 = st.tabs(["Live Signals", "Backtester"])
with tab1:
    live_signal_app()
with tab2:
    backtester_app()
