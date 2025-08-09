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

def safe_generate_signals(df, price_col='Close'):
    """Bulletproof signal generation with full error handling"""
    try:
        df = df.copy()
        
        # Auto-detect suitable price column
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if not numeric_cols.empty:
            price_col = numeric_cols[0]
        
        # Ensure we have valid data
        if price_col not in df.columns or df[price_col].empty:
            raise ValueError("No suitable price column found")
        
        # Convert to numeric safely
        df[price_col] = pd.to_numeric(df[price_col].values, errors='coerce')
        df = df.dropna(subset=[price_col])
        
        if df.empty:
            raise ValueError("No valid numeric data after cleaning")
            
        # Calculate indicators
        df["MA10"] = df[price_col].rolling(10).mean()
        df["MA50"] = df[price_col].rolling(50).mean()
        df["RSI"] = calculate_rsi(df[price_col])
        
        # Generate signals
        df["Signal"] = 0
        df.loc[(df["RSI"] < 30) & (df["MA10"] > df["MA50"]), "Signal"] = 1
        df.loc[(df["RSI"] > 70) & (df["MA10"] < df["MA50"]), "Signal"] = -1
        
        return df, price_col
        
    except Exception as e:
        st.error(f"Signal generation failed: {str(e)}")
        return pd.DataFrame(), None

# --- Live Signal Generator ---
def live_signal_app():
    st.header("📈 Live Signal Generator")
    pair = st.selectbox("Currency Pair", ["EUR/USD", "GBP/USD", "USD/JPY"], key='live_pair')
    
    # Generate realistic synthetic data
    try:
        dates = pd.date_range(end=datetime.now(), periods=100)
        prices = {
            "EUR/USD": 1.08 + np.cumsum(np.random.randn(100) * 0.002),
            "GBP/USD": 1.26 + np.cumsum(np.random.randn(100) * 0.002),
            "USD/JPY": 151.50 + np.cumsum(np.random.randn(100) * 0.2)
        }[pair]
        
        data = pd.DataFrame({"Date": dates, "Price": prices})
        signals, price_col = safe_generate_signals(data, 'Price')
        
        if not signals.empty:
            display_signals(pair, signals, price_col)
            
    except Exception as e:
        st.error(f"Live data error: {str(e)}")

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
            try:
                data = yf.download(pair, period=f"{years}y")
                if not data.empty:
                    signals, price_col = safe_generate_signals(data)
                    if not signals.empty:
                        display_signals(pair.replace("=X", ""), signals, price_col)
                else:
                    st.warning("No data returned from Yahoo Finance")
            except Exception as e:
                st.error(f"Backtest failed: {str(e)}")

# --- Universal Display ---
def display_signals(pair, signals, price_col):
    """Error-proof display function"""
    try:
        latest = signals.iloc[-1]
        price_value = float(latest[price_col])
        
        # Smart decimal formatting
        decimals = 5 if any(p in pair for p in ['JPY', 'XAU']) else 5
        fmt_price = f"{price_value:.{decimals}f}".rstrip('0').rstrip('.')
        
        st.metric(
            label=pair,
            value=fmt_price,
            delta="BUY 🟢" if latest['Signal'] == 1 else "SELL 🔴" if latest['Signal'] == -1 else "HOLD ⚪"
        )
        
        # Prepare chart data
        chart_data = signals[[price_col, "MA10", "MA50"]].copy()
        chart_data.columns = ["Price", "MA(10)", "MA(50)"]
        st.line_chart(chart_data)
        
        # Show recent signals
        with st.expander("Recent Signals"):
            st.dataframe(
                signals.tail(10)[[price_col, 'Signal']].style.apply(
                    lambda x: ['background: lightgreen' if x.Signal == 1 else 
                             'background: lightcoral' if x.Signal == -1 else ''], 
                    axis=1
                )
            )
            
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
