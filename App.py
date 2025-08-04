import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from signal_engine import calculate_indicators, generate_signal

# --------------------------
# Streamlit Page Setup
# --------------------------
st.set_page_config(page_title="Pro Trading Signal Dashboard", layout="wide")
st.title("📊 Professional Trading Signal Dashboard")

# --------------------------
# Sidebar - User Inputs
# --------------------------
st.sidebar.header("⚙ Settings")

symbol = st.sidebar.selectbox("Select Asset/Pair", [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "XAUUSD=X", "BTC-USD"
])
timeframe = st.sidebar.selectbox("Timeframe", ["1h", "4h", "1d"])
days = st.sidebar.slider("History (days)", 7, 60, 30)

rr_ratio = st.sidebar.slider("Risk-Reward Ratio", 1, 5, 2)
atr_multiplier = st.sidebar.slider("ATR Multiplier for Stop Loss", 1.0, 3.0, 1.5)

# --------------------------
# Fetch Market Data
# --------------------------
st.subheader(f"📈 Live Chart: {symbol} ({timeframe})")
data = yf.download(symbol, period=f"{days}d", interval=timeframe)

if data.empty:
    st.error("⚠ No data fetched. Try a different symbol or timeframe.")
    st.stop()

# Calculate Indicators
df = calculate_indicators(data)

# --------------------------
# Plot Candlestick + EMAs + Bollinger
# --------------------------
fig = go.Figure()

# Candlestick
fig.add_trace(go.Candlestick(
    x=df.index, open=df['Open'], high=df['High'],
    low=df['Low'], close=df['Close'],
    name='Price', increasing_line_color='green', decreasing_line_color='red'
))

# EMAs
fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='blue', width=1), name='EMA20'))
fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], line=dict(color='orange', width=1), name='EMA50'))
fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], line=dict(color='red', width=1), name='EMA200'))

# Bollinger Bands
fig.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], line=dict(color='purple', width=1), name='BB Upper', opacity=0.4))
fig.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], line=dict(color='purple', width=1), name='BB Lower', opacity=0.4))

fig.update_layout(
    xaxis_rangeslider_visible=False,
    template="plotly_dark",
    height=600,
)

st.plotly_chart(fig, use_container_width=True)

# --------------------------
# Generate Trading Signal
# --------------------------
st.subheader("📊 Current Signal Recommendation")
signal_info = generate_signal(df, rr_ratio=rr_ratio, atr_multiplier=atr_multiplier)

col1, col2 = st.columns(2)
with col1:
    st.metric("Signal", signal_info["signal"])
    st.metric("Confidence", f"{signal_info['confidence']}%")
with col2:
    st.metric("Entry Price", signal_info["entry"])
    st.metric("Stop-Loss", signal_info["stop_loss"])
    st.metric("Take-Profit", signal_info["take_profit"])

st.info(f"💡 Reason: {signal_info['reason']}")

# --------------------------
# Signal History (Optional)
# --------------------------
st.subheader("📜 Signal History (last 10 bars)")
history = []
for i in range(len(df) - 10, len(df)):
    temp_df = df.iloc[:i+1]
    sig = generate_signal(temp_df, rr_ratio, atr_multiplier)
    history.append([df.index[i], sig["signal"], sig["entry"], sig["stop_loss"], sig["take_profit"]])

hist_df = pd.DataFrame(history, columns=["Time", "Signal", "Entry", "Stop-Loss", "Take-Profit"])
st.dataframe(hist_df, use_container_width=True)
