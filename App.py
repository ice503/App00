import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from signal_engine import calculate_indicators, generate_signal

st.set_page_config(layout="wide")
st.title("📊 Professional Multi-Currency Trading Dashboard")

# --- Sidebar Settings ---
st.sidebar.header("Chart Settings")

currency_pairs = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPY=X",
    "AUD/USD": "AUDUSD=X",
    "USD/CAD": "CAD=X"
}

pair_name = st.sidebar.selectbox("Select Currency Pair", list(currency_pairs.keys()))
symbol = currency_pairs[pair_name]

period = st.sidebar.selectbox("Data Period", ["5d", "1mo", "3mo"], index=0)
interval = st.sidebar.selectbox("Timeframe", ["1h", "30m", "15m"], index=0)
rr_ratio = st.sidebar.slider("Risk/Reward Ratio", 1.0, 5.0, 2.0)
atr_multiplier = st.sidebar.slider("ATR Multiplier (SL distance)", 1.0, 3.0, 1.5)

# --- Fetch Data ---
data = yf.download(symbol, period=period, interval=interval)
if data.empty:
    st.error("No data fetched. Try a different period or interval.")
    st.stop()

# --- Calculate Indicators ---
df = calculate_indicators(data)
signal_info = generate_signal(df, rr_ratio=rr_ratio, atr_multiplier=atr_multiplier)

# --- Plotly Candlestick Chart ---
fig = go.Figure()

# Candlestick
fig.add_trace(go.Candlestick(
    x=df.index,
    open=df["Open"],
    high=df["High"],
    low=df["Low"],
    close=df["Close"],
    name="Price",
    increasing_line_color='green',
    decreasing_line_color='red'
))

# EMA Lines
fig.add_trace(go.Scatter(x=df.index, y=df["EMA20"], line=dict(color="blue", width=1), name="EMA20"))
fig.add_trace(go.Scatter(x=df.index, y=df["EMA50"], line=dict(color="orange", width=1), name="EMA50"))
fig.add_trace(go.Scatter(x=df.index, y=df["EMA200"], line=dict(color="purple", width=1), name="EMA200"))

# Bollinger Bands
fig.add_trace(go.Scatter(x=df.index, y=df["BB_Upper"], line=dict(color="gray", width=1), name="BB Upper", opacity=0.3))
fig.add_trace(go.Scatter(x=df.index, y=df["BB_Lower"], line=dict(color="gray", width=1), name="BB Lower", opacity=0.3))

# --- Interactive Layout ---
fig.update_layout(
    title=f"{pair_name} Live Chart ({interval})",
    xaxis_rangeslider_visible=True,
    dragmode='pan',
    hovermode='x unified',
    template="plotly_dark",
    height=700,
    margin=dict(l=0, r=0, t=40, b=0)
)

# Show Chart
st.plotly_chart(fig, use_container_width=True)

# --- Trading Signal ---
st.subheader(f"📈 Latest Trading Signal for {pair_name}")
st.write(f"**Signal:** {signal_info['signal']} ({signal_info['confidence']}% confidence)")
st.write(f"**Entry:** {signal_info['entry']:.5f}")
if signal_info['stop_loss']:
    st.write(f"**Stop-Loss:** {signal_info['stop_loss']:.5f}")
if signal_info['take_profit']:
    st.write(f"**Take-Profit:** {signal_info['take_profit']:.5f}")
st.write(f"**Reason:** {signal_info['reason']}")
