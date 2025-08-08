import streamlit as st
import pandas as pd
import ta

st.set_page_config(page_title="Trading AI Dashboard", layout="wide")

# ----------------------
# FUNCTIONS
# ----------------------

def generate_signal(df: pd.DataFrame) -> str:
    """Generate a simple RSI-based trading signal."""
    df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
    latest_rsi = df['rsi'].iloc[-1]
    if latest_rsi < 30:
        return "BUY"
    elif latest_rsi > 70:
        return "SELL"
    return "HOLD"

def calculate_risk_levels(df: pd.DataFrame, entry_price: float, risk_ratio: float = 2.0):
    """Calculate stop-loss and take-profit using ATR."""
    atr = ta.volatility.AverageTrueRange(
        df['high'], df['low'], df['close']
    ).average_true_range().iloc[-1]
    
    stop_loss = entry_price - atr
    take_profit = entry_price + atr * risk_ratio
    return stop_loss, take_profit

def calculate_performance():
    """Mock performance metrics. Extend with real backtesting results."""
    return {
        "Win Rate": "65%",
        "Max Drawdown": "12%",
        "Risk/Reward": "1:2.5"
    }

def scan_multi_timeframe(symbol: str):
    """Mock multi-timeframe signal. Extend with real data sources."""
    return {
        "M15": "BUY",
        "H1": "HOLD",
        "H4": "BUY",
        "Convergence": "BULLISH"
    }

# ----------------------
# STREAMLIT UI
# ----------------------

st.sidebar.header("Trading Settings")
symbol = st.sidebar.selectbox("Symbol", ["EURUSD", "GBPUSD", "XAUUSD"])
timeframe = st.sidebar.selectbox("Timeframe", ["M15", "H1", "H4"])
risk_ratio = st.sidebar.slider("Risk/Reward Ratio", 1.0, 5.0, 2.0)

st.title("📊 Trading AI Dashboard")

# Simulated data (replace with live feed later)
df = pd.DataFrame({
    "close": [1.10, 1.105, 1.102, 1.108],
    "high": [1.11, 1.106, 1.104, 1.109],
    "low": [1.09, 1.103, 1.100, 1.107]
})

# Generate Signal
signal = generate_signal(df)
st.subheader(f"Real-Time Signal: {signal}")

# Calculate Risk Levels
entry_price = df["close"].iloc[-1]
sl, tp = calculate_risk_levels(df, entry_price, risk_ratio)
st.write(f"**Entry Price:** {entry_price:.5f}")
st.write(f"**Stop-Loss:** {sl:.5f}")
st.write(f"**Take-Profit:** {tp:.5f}")

# Multi-Timeframe Scan
st.subheader("Multi-Timeframe Convergence")
convergence = scan_multi_timeframe(symbol)
st.write(convergence)

# Performance Analytics (Sample)
st.subheader("Performance Analytics")
metrics = calculate_performance()
st.write(metrics)

st.success("✅ Dashboard loaded successfully!")
