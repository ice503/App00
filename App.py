import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from signal_engine import calculate_indicators, generate_signal

st.set_page_config(page_title="Pro Trading Signal Dashboard", layout="wide")

st.title("📊 Professional Trading Signal Dashboard")
st.markdown("Analyze live EUR/USD 1-hour data with technical indicators and get signals.")

# Select symbol
symbol = st.selectbox("Select currency pair:", ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X"], index=0)
interval = "1h"
period = "7d"

# Download data
@st.cache_data(ttl=600)
def load_data(sym, per, intrvl):
    data = yf.download(sym, period=per, interval=intrvl)
    return data

data = load_data(symbol, period, interval)

if data.empty:
    st.error("No data retrieved. Try again later or change the symbol.")
    st.stop()

# Calculate indicators
try:
    df = calculate_indicators(data)
except Exception as e:
    st.error(f"Error calculating indicators: {e}")
    st.stop()

# Generate signal
signal_info = generate_signal(df)

# Show candlestick chart with indicators
def plot_candlestick(df):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Candlesticks"
    ))

    # EMA lines
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA20"], line=dict(color="blue", width=1), name="EMA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA50"], line=dict(color="orange", width=1), name="EMA50"))
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA200"], line=dict(color="green", width=1), name="EMA200"))

    # Bollinger Bands
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_Upper"], line=dict(color="gray", width=1, dash='dot'), name="BB Upper", opacity=0.5))
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_Lower"], line=dict(color="gray", width=1, dash='dot'), name="BB Lower", opacity=0.5))

    fig.update_layout(
        title=f"{symbol} Price Chart with Indicators",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        height=600,
        template="plotly_dark",
        hovermode="x unified"
    )
    return fig

fig = plot_candlestick(df)
st.plotly_chart(fig, use_container_width=True)

# Show latest signal info
st.markdown("## Latest Trade Signal")
st.write(f"**Signal:** {signal_info['signal']}")
if signal_info["signal"] in ["BUY", "SELL"]:
    st.write(f"**Stop Loss:** {signal_info['stop_loss']}")
    st.write(f"**Take Profit:** {signal_info['take_profit']}")

# Show raw data toggle
if st.checkbox("Show raw data"):
    st.dataframe(df.tail(20))
