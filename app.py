import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

# --- Core Strategy Functions ---
def calculate_rsi(series, window=14):
    """Safe RSI calculation with input validation"""
    if not isinstance(series, (pd.Series, np.ndarray, list)):
        raise ValueError("RSI input must be a Series, array, or list")
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def safe_to_numeric(data):
    """Convert input to numeric with comprehensive validation"""
    if isinstance(data, (pd.Series, pd.DataFrame)):
        return pd.to_numeric(data, errors='coerce')
    elif isinstance(data, (np.ndarray, list, tuple)):
        return pd.to_numeric(pd.Series(data), errors='coerce')
    else:
        try:
            return pd.to_numeric([data], errors='coerce')[0]
        except:
            return np.nan

def generate_signals(df, price_col='Close'):
    """Robust signal generation with full error handling"""
    try:
        # Create working copy and validate
        df = df.copy()
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input must be a DataFrame")
            
        # Auto-detect price column if needed
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if price_col not in df.columns and len(numeric_cols) > 0:
            price_col = numeric_cols[0]
            
        # Validate column exists
        if price_col not in df.columns:
            raise ValueError(f"Price column '{price_col}' not found")
            
        # Convert to numeric safely
        df[price_col] = safe_to_numeric(df[price_col])
        df = df.dropna(subset=[price_col])
        
        if df.empty:
            raise ValueError("No valid price data after cleaning")
            
        # Calculate indicators
        df["MA10"] = df[price_col].rolling(10).mean()
        df["MA50"] = df[price_col].rolling(50).mean()
        df["RSI"] = calculate_rsi(df[price_col])
        
        # Generate signals with explicit masks
        buy_mask = (df["RSI"] < 30) & (df["MA10"] > df["MA50"])
        sell_mask = (df["RSI"] > 70) & (df["MA10"] < df["MA50"])
        
        df["Signal"] = 0
        df.loc[buy_mask, "Signal"] = 1
        df.loc[sell_mask, "Signal"] = -1
        
        return df, price_col
        
    except Exception as e:
        st.error(f"Signal generation error: {str(e)}")
        return pd.DataFrame(), None

# --- UI Components ---
def display_signals(pair, signals, price_col):
    """Error-proof signal display"""
    try:
        if signals.empty or price_col not in signals.columns:
            raise ValueError("No valid signals to display")
            
        latest = signals.iloc[-1]
        
        # Format price appropriately
        is_jpy = "JPY" in pair
        price_value = latest[price_col]
        price_fmt = f"{price_value:.2f}" if is_jpy else f"{price_value:.5f}"
        
        # Determine signal display
        signal_val = latest.get('Signal', 0)
        if not isinstance(signal_val, (int, float)):
            signal_val = 0
        signal_display = ("BUY 🟢" if signal_val == 1 else 
                         "SELL 🔴" if signal_val == -1 else 
                         "HOLD ⚪")
        
        # Show metrics
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric(pair, price_fmt, delta=signal_display)
            st.caption(f"RSI: {latest.get('RSI', 'N/A'):.1f}")
            st.caption(f"MA10/50: {latest.get('MA10', 'N/A'):.5f}/{latest.get('MA50', 'N/A'):.5f}")
            
        with col2:
            chart_cols = [price_col, 'MA10', 'MA50']
            valid_cols = [c for c in chart_cols if c in signals.columns]
            if valid_cols:
                st.line_chart(signals[valid_cols].rename(columns={
                    price_col: "Price",
                    'MA10': "MA(10)",
                    'MA50': "MA(50)"
                }))
                
        # Show history
        with st.expander("Recent Signals"):
            hist_cols = [c for c in ['Date', price_col, 'Signal'] if c in signals.columns]
            if hist_cols:
                st.dataframe(
                    signals[hist_cols].tail(10).style.apply(
                        lambda row: ['background: lightgreen' if row.Signal == 1 else
                                   'background: lightcoral' if row.Signal == -1 else
                                   '' for _ in row],
                        axis=1
                    )
                )
                
    except Exception as e:
        st.error(f"Display error: {str(e)}")

# --- Main App ---
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
        signals, price_col = generate_signals(data, 'Price')
        
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
                    signals, price_col = generate_signals(data)
                    if not signals.empty and price_col:
                        display_signals(pair.replace("=X", ""), signals, price_col)
                else:
                    st.warning("No data returned from API")
            except Exception as e:
                st.error(f"Backtest failed: {str(e)}")

# --- App Setup ---
st.set_page_config(layout="wide")
st.title("Forex Signal Analyzer")

tab1, tab2 = st.tabs(["Live Signals", "Backtester"])
with tab1:
    live_signal_app()
with tab2:
    backtester_app()
