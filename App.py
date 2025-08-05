import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from signal_engine import calculate_indicators, generate_signals

st.set_page_config(page_title="Pro Trading Signals", layout="wide")

st.title("📊 Professional Trading Signal Dashboard")

# Sidebar for user selection
st.sidebar.header("Settings")
symbol = st.sidebar.selectbox("Currency Pair", ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X"])
timeframe = st.sidebar.selectbox("Timeframe", ["1h", "4h", "1d"])
period = st.sidebar.number_input("Lookback Days", min_value=5, max_value=365, value=30)

st.write(f"📈 Live Candlestick Chart: **{symbol}** ({timeframe})")

# Fetch historical data
data = yf.download(tickers=symbol, period=f"{period}d", interval=timeframe)
data.dropna(inplace=True)

if data.empty:
    st.error("No data available. Try a different symbol or timeframe.")
else:
    # Calculate indicators and generate signals
    df = calculate_indicators(data)
    df = generate_signals(df)

    # Candlestick chart
    fig = go.Figure(data=[
        go.Candlestick(
            x=df.index,
            open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
            name="Price"
        )
    ])

    # Add Buy and Sell signals
    buy_signals = df[df["Signal"] == "BUY"]
    sell_signals = df[df["Signal"] == "SELL"]

    fig.add_trace(go.Scatter(
        x=buy_signals.index,
        y=buy_signals["Close"],
        mode="markers",
        name="Buy Signal",
        marker=dict(symbol="triangle-up", color="green", size=12)
    ))

    fig.add_trace(go.Scatter(
        x=sell_signals.index,
        y=sell_signals["Close"],
        mode="markers",
        name="Sell Signal",
        marker=dict(symbol="triangle-down", color="red", size=12)
    ))

    # Stop Loss and Take Profit levels for the last signal
    if not buy_signals.empty or not sell_signals.empty:
        last_signal = df[df["Signal"].isin(["BUY", "SELL"])].iloc[-1]
        st.subheader("📢 Latest Signal")
        st.write(f"**Signal:** {last_signal['Signal']}")
        st.write(f"**Price:** {last_signal['Close']:.5f}")
        if "StopLoss" in last_signal and "TakeProfit" in last_signal:
            st.write(f"**Stop Loss:** {last_signal['StopLoss']:.5f}")
            st.write(f"**Take Profit:** {last_signal['TakeProfit']:.5f}")

    # Chart layout
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=600,
        template="plotly_dark",
        title=f"Trading Signals for {symbol}",
        yaxis_title="Price"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Show table of signals
    st.subheader("Historical Signals")
    st.dataframe(df[["Close", "Signal", "StopLoss", "TakeProfit"]].tail(20))
