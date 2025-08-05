import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from signal_engine import calculate_indicators, generate_signal

# -------------------------
# Streamlit Page Setup
# -------------------------
st.set_page_config(page_title="Professional Trading Dashboard", layout="wide")

st.title("📊 Professional Trading Signal Dashboard")

# Sidebar for settings
st.sidebar.header("Settings")
symbol = st.sidebar.text_input("Symbol (Yahoo Finance format):", value="EURUSD=X")
interval = st.sidebar.selectbox("Interval", ["1h", "30m", "15m", "5m", "1d"])
lookback = st.sidebar.number_input("Lookback candles", min_value=50, max_value=2000, value=500)
rr_ratio = st.sidebar.slider("Risk-Reward Ratio", 1.0, 5.0, 2.0, 0.1)
atr_multiplier = st.sidebar.slider("ATR Multiplier (for SL/TP)", 0.5, 3.0, 1.5, 0.1)

# -------------------------
# Fetch Data
# -------------------------
st.write(f"📈 Live Chart: {symbol} ({interval})")

try:
    data = yf.download(tickers=symbol, period="60d", interval=interval)
    if data.empty:
        st.error("No data retrieved. Try another symbol or interval.")
        st.stop()

    # Rename columns for consistency
    data = data.rename(columns={"Open": "Open", "High": "High", "Low": "Low", "Close": "Close", "Volume": "Volume"})
    df = calculate_indicators(data.tail(lookback))

    # -------------------------
    # Plot Candlestick Chart with Indicators
    # -------------------------
    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Price"
    ))

    # EMA Lines
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA20"], mode="lines", name="EMA20", line=dict(color="blue", width=1)))
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA50"], mode="lines", name="EMA50", line=dict(color="orange", width=1)))
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA200"], mode="lines", name="EMA200", line=dict(color="green", width=1)))

    # Bollinger Bands
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_Upper"], line=dict(color="gray", width=1), name="BB Upper", opacity=0.5))
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_Lower"], line=dict(color="gray", width=1), name="BB Lower", opacity=0.5))

    # Layout
    fig.update_layout(
        title=f"{symbol} Candlestick Chart",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=700,
        dragmode="pan"
    )

    st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # Trading Signal
    # -------------------------
    signal_info = generate_signal(df, rr_ratio=rr_ratio, atr_multiplier=atr_multiplier)
    st.subheader("📢 Latest Signal")
    st.text(signal_info)

except Exception as e:
    st.error(f"Error generating chart: {e}")
