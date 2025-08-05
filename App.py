import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from signal_engine import calculate_indicators, generate_signal

st.set_page_config(page_title="📊 Professional Trading Signal Dashboard", layout="wide")

st.title("📊 Professional Trading Signal Dashboard")

# --- Sidebar controls ---
st.sidebar.header("Settings")
pair = st.sidebar.selectbox("Currency Pair", ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X"])
period = st.sidebar.selectbox("Period", ["1d","5d","1mo","3mo"])
interval = st.sidebar.selectbox("Interval", ["1h","30m","15m","5m","1d"])

rr_ratio = st.sidebar.slider("Risk/Reward Ratio", 1.0, 5.0, 2.0, 0.1)
atr_multiplier = st.sidebar.slider("ATR Multiplier (for Stop Loss)", 0.5, 3.0, 1.5, 0.1)

# --- Fetch Data ---
data = yf.download(pair, period=period, interval=interval)

if data.empty:
    st.error("No data found for this pair and timeframe.")
    st.stop()

data.reset_index(inplace=True)
data.rename(columns={
    'Open': 'Open',
    'High': 'High',
    'Low': 'Low',
    'Close': 'Close'
}, inplace=True)

# --- Calculate Indicators ---
df = calculate_indicators(data)

# --- Generate Signal ---
signal_info = generate_signal(df, rr_ratio=rr_ratio, atr_multiplier=atr_multiplier)

st.subheader(f"Latest Signal for {pair}")
st.write(signal_info)

# --- Candlestick Chart with Plotly (Interactive) ---
fig = go.Figure(data=[
    go.Candlestick(
        x=df['Datetime'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="Candlestick"
    )
])

# Add EMA lines
fig.add_trace(go.Scatter(x=df['Datetime'], y=df['EMA20'], line=dict(color='blue', width=1), name='EMA20'))
fig.add_trace(go.Scatter(x=df['Datetime'], y=df['EMA50'], line=dict(color='orange', width=1), name='EMA50'))
fig.add_trace(go.Scatter(x=df['Datetime'], y=df['EMA200'], line=dict(color='red', width=1), name='EMA200'))

# Add Bollinger Bands
fig.add_trace(go.Scatter(x=df['Datetime'], y=df['BB_Upper'], line=dict(color='gray', width=1, dash='dot'), name='BB Upper'))
fig.add_trace(go.Scatter(x=df['Datetime'], y=df['BB_Lower'], line=dict(color='gray', width=1, dash='dot'), name='BB Lower'))

fig.update_layout(
    xaxis_rangeslider_visible=False,
    template='plotly_dark',
    height=700,
    hovermode='x unified'
)

st.plotly_chart(fig, use_container_width=True)
