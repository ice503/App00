import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from signal_engine import calculate_indicators, generate_signals

# -----------------------
# Streamlit App Settings
# -----------------------
st.set_page_config(page_title="Pro Trading Dashboard", layout="wide")
st.title("📊 Professional Trading Signal Dashboard")

# Currency pairs to choose from
pairs = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPY=X",
    "XAU/USD (Gold)": "XAUUSD=X"
}

# Sidebar settings
st.sidebar.header("Settings")
pair = st.sidebar.selectbox("Select Currency Pair", list(pairs.keys()))
interval = st.sidebar.selectbox("Select Timeframe", ["1h", "4h", "1d"])
history_period = st.sidebar.slider("History (days)", 5, 60, 30)
rr_ratio = st.sidebar.slider("Risk-Reward Ratio", 1.0, 3.0, 2.0)
atr_multiplier = st.sidebar.slider("ATR Multiplier for Stop-Loss", 1.0, 3.0, 1.5)

# -----------------------
# Fetch & Calculate Data
# -----------------------
st.write(f"📈 **Live Chart:** {pair} ({interval})")

symbol = pairs[pair]

try:
    data = yf.download(symbol, period=f"{history_period}d", interval=interval)
    data.reset_index(inplace=True)

    if data.empty:
        st.error("No data returned. Try a different pair or timeframe.")
    else:
        # Calculate indicators & signals
        df = calculate_indicators(data)
        df = generate_signals(df, rr_ratio=rr_ratio, atr_multiplier=atr_multiplier)

        # -----------------------
        # Plot Candlestick Chart
        # -----------------------
        fig = go.Figure()

        # Candlestick
        fig.add_trace(go.Candlestick(
            x=df['Date'] if 'Date' in df.columns else df['Datetime'],
            open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'],
            name="Candles"
        ))

        # EMAs
        fig.add_trace(go.Scatter(x=df.index, y=df["EMA20"], line=dict(color='blue', width=1), name="EMA 20"))
        fig.add_trace(go.Scatter(x=df.index, y=df["EMA50"], line=dict(color='orange', width=1), name="EMA 50"))
        fig.add_trace(go.Scatter(x=df.index, y=df["EMA200"], line=dict(color='red', width=1), name="EMA 200"))

        # Bollinger Bands
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_Upper"], line=dict(color='gray', width=1), name="BB Upper", opacity=0.4))
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_Lower"], line=dict(color='gray', width=1), name="BB Lower", opacity=0.4))

        # Buy / Sell markers
        buys = df[df["Signal"] == "BUY"]
        sells = df[df["Signal"] == "SELL"]

        fig.add_trace(go.Scatter(
            x=buys.index, y=buys["Close"], mode="markers",
            marker=dict(color="green", size=10, symbol="triangle-up"),
            name="Buy Signal"
        ))
        fig.add_trace(go.Scatter(
            x=sells.index, y=sells["Close"], mode="markers",
            marker=dict(color="red", size=10, symbol="triangle-down"),
            name="Sell Signal"
        ))

        fig.update_layout(
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            title=f"{pair} Trading Dashboard",
            yaxis_title="Price",
            hovermode="x unified",
            height=700
        )

        st.plotly_chart(fig, use_container_width=True)

        # -----------------------
        # Show Latest Signal
        # -----------------------
        latest_signal = df.iloc[-1][["Signal", "StopLoss", "TakeProfit"]]
        st.subheader("📢 Latest Signal")
        st.write(latest_signal.to_frame().T)

        # -----------------------
        # Show Recent Signals Table
        # -----------------------
        st.subheader("📜 Recent Signals")
        signals = df[df["Signal"] != ""].tail(10)
        st.dataframe(signals[["Signal", "Close", "StopLoss", "TakeProfit"]])

except Exception as e:
    st.error(f"Error: {e}")
