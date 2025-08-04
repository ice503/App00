import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from streamlit_lightweight_charts import renderLightweightCharts
from signal_engine import calculate_indicators, generate_signal

st.set_page_config(layout="wide")
st.title("📊 Professional Trading Signal Dashboard")

# --- Sidebar settings ---
st.sidebar.header("Settings")
symbol = st.sidebar.text_input("Symbol", value="EURUSD=X")  # Yahoo Finance symbol
interval = st.sidebar.selectbox("Timeframe", ["1h", "30m", "15m", "5m", "1d"], index=0)
period = st.sidebar.selectbox("Data Period", ["5d", "1mo", "3mo"], index=0)
rr_ratio = st.sidebar.slider("Risk/Reward Ratio", 1.0, 5.0, 2.0, 0.5)
atr_multiplier = st.sidebar.slider("ATR Multiplier (for SL/TP)", 1.0, 3.0, 1.5, 0.1)

# --- Download data ---
data = yf.download(symbol, period=period, interval=interval)
if data.empty:
    st.error("No data found for this symbol/timeframe.")
    st.stop()

# --- Calculate Indicators and Signals ---
df = calculate_indicators(data)
signal_info = generate_signal(df, rr_ratio=rr_ratio, atr_multiplier=atr_multiplier)

st.subheader(f"Latest Signal for {symbol}")
st.write(f"""
**Signal:** {signal_info['signal']}  
**Confidence:** {signal_info['confidence']}%  
**Entry:** {signal_info['entry']}  
**Stop Loss:** {signal_info['stop_loss']}  
**Take Profit:** {signal_info['take_profit']}  
**Reason:** {signal_info['reason']}
""")

# --- Prepare TradingView-like candlestick chart ---
df = df.tail(200)  # Show last 200 candles

# Candlestick data
candles = [
    {
        "time": str(idx),
        "open": row["Open"],
        "high": row["High"],
        "low": row["Low"],
        "close": row["Close"],
    }
    for idx, row in df.iterrows()
]

# EMA lines
ema20 = [{"time": str(idx), "value": row["EMA20"]} for idx, row in df.iterrows()]
ema50 = [{"time": str(idx), "value": row["EMA50"]} for idx, row in df.iterrows()]
ema200 = [{"time": str(idx), "value": row["EMA200"]} for idx, row in df.iterrows()]

# Signal lines for SL/TP
signal_lines = []
if signal_info["signal"] != "HOLD":
    signal_lines.append({
        "type": "Line",
        "data": [{"time": str(df.index[-1]), "value": signal_info["stop_loss"]}],
        "color": "red",
        "lineWidth": 2
    })
    signal_lines.append({
        "type": "Line",
        "data": [{"time": str(df.index[-1]), "value": signal_info["take_profit"]}],
        "color": "green",
        "lineWidth": 2
    })

chart_options = [
    {
        "chart": {
            "layout": {"background": {"type": "solid", "color": "#000000"}, "textColor": "#FFFFFF"},
            "grid": {"vertLines": {"color": "#222"}, "horzLines": {"color": "#222"}},
        },
        "series": [
            {
                "type": "Candlestick",
                "data": candles,
                "upColor": "#26a69a",
                "downColor": "#ef5350",
                "borderVisible": False,
                "wickUpColor": "#26a69a",
                "wickDownColor": "#ef5350",
            },
            {"type": "Line", "data": ema20, "color": "yellow", "lineWidth": 2},
            {"type": "Line", "data": ema50, "color": "orange", "lineWidth": 2},
            {"type": "Line", "data": ema200, "color": "blue", "lineWidth": 2},
        ] + signal_lines
    }
]

renderLightweightCharts(chart_options, key="chart")
