import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from signal_engine import calculate_indicators, generate_signal

# =======================
# Streamlit Page Config
# =======================
st.set_page_config(page_title="Pro Trading Dashboard", layout="wide")
st.title("📊 Professional Trading Signal Dashboard")

# User Inputs
pair = st.sidebar.text_input("Enter Symbol", value="EURUSD=X")
timeframe = st.sidebar.selectbox("Timeframe", ["1h", "4h", "1d"], index=0)
period = st.sidebar.selectbox("Lookback Period", ["1mo", "3mo", "6mo"], index=0)
rr_ratio = st.sidebar.slider("Risk-Reward Ratio", 1.0, 5.0, 2.0)
atr_multiplier = st.sidebar.slider("ATR Multiplier (for SL)", 0.5, 3.0, 1.5)

# =======================
# Fetch Market Data
# =======================
st.write(f"📈 Live Chart: **{pair}** ({timeframe})")

try:
    data = yf.download(pair, period=period, interval=timeframe)
    data.dropna(inplace=True)

    if data.empty:
        st.error("No data retrieved. Check symbol or timeframe.")
        st.stop()

    df = calculate_indicators(data)
    signal_info = generate_signal(df, rr_ratio=rr_ratio, atr_multiplier=atr_multiplier)

    # =======================
    # TradingView-like Chart
    # =======================
    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Candles',
        increasing_line_color='green',
        decreasing_line_color='red'
    ))

    # EMA Lines
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='yellow', width=1), name='EMA 20'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], line=dict(color='orange', width=1), name='EMA 50'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], line=dict(color='blue', width=2), name='EMA 200'))

    # Bollinger Bands
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], line=dict(color='lightblue', width=1, dash='dot'), name='BB Upper'))
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], line=dict(color='lightblue', width=1, dash='dot'), name='BB Lower'))

    fig.update_layout(
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        height=600,
        margin=dict(l=10, r=10, t=40, b=10),
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)

    # =======================
    # Signal Info Display
    # =======================
    st.subheader("💡 Signal Suggestion")
    st.write(f"**Signal:** {signal_info['signal']}")
    st.write(f"**Confidence:** {signal_info['confidence']}%")
    st.write(f"**Entry Price:** {signal_info['entry']}")
    st.write(f"**Stop Loss:** {signal_info['stop_loss']}")
    st.write(f"**Take Profit:** {signal_info['take_profit']}")
    st.write(f"**Reason:** {signal_info['reason']}")

except Exception as e:
    st.error(f"Error loading chart: {e}")
