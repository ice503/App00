import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

# --- Data Validation Utilities ---
def ensure_series(data):
    """Convert any input to pandas Series safely"""
    if isinstance(data, pd.Series):
        return data
    elif isinstance(data, (np.ndarray, list, tuple)):
        return pd.Series(data)
    elif isinstance(data, (int, float)):
        return pd.Series([data])
    else:
        try:
            return pd.Series(data)
        except:
            return pd.Series(dtype='float64')

def safe_numeric(data):
    """Convert input to numeric with comprehensive validation"""
    series = ensure_series(data)
    return pd.to_numeric(series, errors='coerce').dropna()

# --- Core Strategy Functions ---
def calculate_rsi(price_data, window=14):
    """Bulletproof RSI calculation"""
    prices = safe_numeric(price_data)
    if len(prices) < window:
        return pd.Series(np.nan, index=prices.index)
    
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def generate_signals(df, price_col='Close'):
    """Completely robust signal generation"""
    try:
        # Create safe working copy
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input must be a DataFrame")
        df = df.copy()
        
        # Auto-detect price column if needed
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if price_col not in df.columns and numeric_cols:
            price_col = numeric_cols[0]
        
        # Validate column exists
        if price_col not in df.columns:
            available_cols = ', '.join(df.columns.tolist())
            raise ValueError(f"Price column '{price_col}' not found. Available columns: {available_cols}")
            
        # Convert to numeric safely
        df[price_col] = safe_numeric(df[price_col])
        if df[price_col].empty:
            raise ValueError(f"No valid numeric data in column '{price_col}'")
            
        # Calculate indicators
        df["MA10"] = df[price_col].rolling(10).mean()
        df["MA50"] = df[price_col].rolling(50).mean()
        df["RSI"] = calculate_rsi(df[price_col])
        
        # Generate signals
        df["Signal"] = 0
        buy_mask = (df["RSI"] < 30) & (df["MA10"] > df["MA50"])
        sell_mask = (df["RSI"] > 70) & (df["MA10"] < df["MA50"])
        
        df.loc[buy_mask, "Signal"] = 1
        df.loc[sell_mask, "Signal"] = -1
        
        return df, price_col
        
    except Exception as e:
        st.error(f"Signal generation failed: {str(e)}")
        return pd.DataFrame(), None

# --- UI Components ---
def display_signals(pair, signals, price_col):
    """Error-proof display with graceful degradation"""
    try:
        if signals.empty or price_col not in signals.columns:
            raise ValueError("No valid signals to display")
            
        latest = signals.iloc[-1]
        
        # Smart formatting
        is_jpy = "JPY" in pair
        price_value = latest[price_col]
        price_fmt = f"{price_value:.3f}" if is_jpy else f"{price_value:.5f}"
        
        # Safe signal display
        signal_val = latest.get('Signal', 0)
        if not isinstance(signal_val, (int, float)):
            signal_val = 0
            
        signal_text = ("BUY 🟢" if signal_val == 1 else
                      "SELL 🔴" if signal_val == -1 else
                      "HOLD ⚪")
        
        # Display metrics
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric(label=pair, value=price_fmt, delta=signal_text)
            st.caption(f"RSI: {latest.get('RSI', 'N/A'):.1f}")
            st.caption(f"MA10: {latest.get('MA10', 'N/A'):.5f}")
            
        with col2:
            chart_data = signals[[price_col, "MA10", "MA50"]].copy()
            chart_data.columns = ["Price", "MA(10)", "MA(50)"]
            st.line_chart(chart_data)
            
        # Show history
        with st.expander("Recent Signals"):
            hist_cols = [c for c in [signals.index.name, price_col, 'Signal'] if c in signals.columns]
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
    pair = st.selectbox("Currency Pair", ["EUR/USD", "GBP/USD", "USD/JPY"], key='live_pair')
    
    try:
        # Generate synthetic data (FIXED missing parenthesis)
        dates = pd.date_range(end=datetime.now(), periods=100)
        prices = {
            "EUR/USD": 1.08 + np.cumsum(np.random.randn(100) * 0.002),
            "GBP/USD": 1.26 + np.cumsum(np.random.randn(100) * 0.002),
            "USD/JPY": 151.50 + np.cumsum(np.random.randn(100) * 0.2)
        }[pair]
        
        data = pd.DataFrame({
            "Date": dates,
            "Price": prices,
            "High": prices + 0.001,
            "Low": prices - 0.001
        }).set_index('Date')
        
        signals, price_col = generate_signals(data, 'Price')
        if not signals.empty and price_col:
            display_signals(pair, signals, price_col)
            
    except Exception as e:
        st.error(f"Live signal error: {str(e)}")

def backtester_app():
    st.header("🔍 Strategy Backtester")
    
    col1, col2 = st.columns(2)
    with col1:
        pair = st.selectbox("Pair", ["EURUSD=X", "GBPUSD=X", "USDJPY=X"], key='backtest_pair')
    with col2:
        years = st.slider("Test Period", 1, 5, 2, key='years')
    
    if st.button("Run Backtest"):
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
st.title("Forex Trading Analyzer")

tab1, tab2 = st.tabs(["Live Signals", "Backtester"])
with tab1:
    live_signal_app()
with tab2:
    backtester_app()
