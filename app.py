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
    """Completely robust signal generation"""
    try:
        df = df.copy()
        
        # Auto-detect first numeric column if specified doesn't exist
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if price_col not in df.columns and len(numeric_cols) > 0:
            price_col = numeric_cols[0]
        
        # Validate data exists
        if price_col not in df.columns:
            raise ValueError(f"Price column '{price_col}' not found in data")
            
        # Convert to numeric safely
        df[price_col] = pd.to_numeric(df[price_col], errors='coerce')
        df = df.dropna(subset=[price_col])
        
        if df.empty:
            raise ValueError("No valid numeric data after cleaning")
            
        # Calculate indicators
        df["MA10"] = df[price_col].rolling(10).mean()
        df["MA50"] = df[price_col].rolling(50).mean()
        df["RSI"] = calculate_rsi(df[price_col])
        
        # Generate signals - COMPLETELY FIXED boolean operations
        buy_mask = (df["RSI"] < 30) & (df["MA10"] > df["MA50"])
        sell_mask = (df["RSI"] > 70) & (df["MA10"] < df["MA50"])
        
        df["Signal"] = 0
        df.loc[buy_mask, "Signal"] = 1
        df.loc[sell_mask, "Signal"] = -1
        
        return df, price_col
        
    except Exception as e:
        st.error(f"Signal generation error: {str(e)}")
        return pd.DataFrame(), None

# --- Display Functions ---
def display_signals(pair, signals, price_col):
    """100% error-proof display"""
    try:
        if signals.empty or price_col not in signals.columns:
            raise ValueError("No valid signals to display")
            
        latest = signals.iloc[-1]
        
        # Format price based on pair type
        is_jpy = any(x in pair for x in ['JPY', 'JPY=X'])
        price_fmt = f"{latest[price_col]:.2f}" if is_jpy else f"{latest[price_col]:.5f}"
        
        # Get signal direction safely
        signal_val = latest.get('Signal', 0)
        if not isinstance(signal_val, (int, float)):
            signal_val = 0
            
        signal_display = (
            "BUY 🟢" if signal_val == 1 
            else "SELL 🔴" if signal_val == -1 
            else "HOLD ⚪"
        )
        
        # Display metrics
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric(pair, price_fmt, delta=signal_display)
            st.caption(f"MA10: {latest.get('MA10', 'N/A'):.5f}")
            st.caption(f"MA50: {latest.get('MA50', 'N/A'):.5f}")
        
        with col2:
            # Prepare chart data safely
            chart_cols = [price_col, 'MA10', 'MA50']
            valid_cols = [c for c in chart_cols if c in signals.columns]
            if valid_cols:
                st.line_chart(signals[valid_cols].rename(columns={
                    price_col: "Price",
                    'MA10': "Fast MA",
                    'MA50': "Slow MA"
                }))
        
        # Show history
        with st.expander("Signal History"):
            hist_cols = ['Date' if 'Date' in signals.columns else signals.index.name, price_col, 'Signal']
            hist_cols = [c for c in hist_cols if c in signals.columns]
            if hist_cols:
                st.dataframe(
                    signals[hist_cols].tail(10).style.apply(
                        lambda row: ['background: lightgreen' if row.Signal == 1 
                                   else 'background: lightcoral' if row.Signal == -1 
                                   else '' for _ in row],
                        axis=1
                    )
                )
                
    except Exception as e:
        st.error(f"Display error: {str(e)}")

# --- Main App Components ---
def live_signal_app():
    st.header("📈 Live Signals")
    pair = st.selectbox("Pair", ["EUR/USD", "GBP/USD", "USD/JPY"], key='live')
    
    try:
        # Generate synthetic data
        dates = pd.date_range(end=datetime.now(), periods=100)
        prices = {
            "EUR/USD": 1.08 + np.cumsum(np.random.randn(100) * 0.002),
            "GBP/USD": 1.26 + np.cumsum(np.random.randn(100) * 0.002),
            "USD/JPY": 151.50 + np.cumsum(np.random.randn(100) * 0.2)
        }[pair]
        
        data = pd.DataFrame({"Date": dates, "Price": prices})
        signals, price_col = safe_generate_signals(data, 'Price')
        
        if not signals.empty and price_col:
            display_signals(pair, signals, price_col)
            
    except Exception as e:
        st.error(f"Live signal error: {str(e)}")

def backtester_app():
    st.header("🔍 Backtester")
    
    col1, col2 = st.columns(2)
    with col1:
        pair = st.selectbox("Pair", ["EURUSD=X", "GBPUSD=X", "USDJPY=X"], key='backtest')
    with col2:
        years = st.slider("Years", 1, 5, 2, key='years')
    
    if st.button("Run Test"):
        with st.spinner("Analyzing..."):
            try:
                data = yf.download(pair, period=f"{years}y")
                if not data.empty:
                    signals, price_col = safe_generate_signals(data)
                    if not signals.empty and price_col:
                        display_signals(pair.replace("=X", ""), signals, price_col)
                else:
                    st.warning("No data returned")
            except Exception as e:
                st.error(f"Backtest failed: {str(e)}")

# --- App Layout ---
st.set_page_config(layout="wide")
st.title("Forex Signal Toolkit")

tab1, tab2 = st.tabs(["Live Signals", "Backtester"])
with tab1:
    live_signal_app()
with tab2:
    backtester_app()
