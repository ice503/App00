import streamlit as st
import pandas as pd
import yfinance as yf
from signal_engine import calculate_indicators, generate_signal
import plotly.graph_objects as go

st.set_page_config(page_title="Professional Trading Dashboard", layout="wide")

st.title("📊 Professional Trading Signal Dashboard")
st.write("Welcome! Select a currency pair and timeframe to generate signals.")

# Step 1: Pair & Timeframe selection
pair = st.selectbox(
    "Select Currency Pair",
    ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "XAUUSD=X", "BTC-USD"]
)
timeframe = st.selectbox(
    "Select Timeframe",
    ["15m", "1h", "4h", "1d"]
)
start_date = st.date_input("Start Date", pd.to_datetime("2024-01-01"))

# Step 2: Button to load data
if st.button("🔄 Load Data & Generate Signals"):
    with st.spinner("Fetching data and calculating indicators..."):
        # Fetch data
        data = yf.download(pair, start=start_date, interval=timeframe)

        if data.empty:
            st.error("No data fetched. Try a different pair or timeframe.")
        else:
            # Calculate indicators
            df = calculate_indicators(data)

            # Generate signal
            signal_info = generate_signal(df)

            # Display signal
            st.subheader(f"Latest Signal for {pair}")
            st.write(signal_info)

            # Step 3: Plot candlestick chart
            fig = go.Figure(data=[go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Candlestick'
            )])

            # Add indicators
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], mode='lines', name='EMA20', line=dict(color='blue')))
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], mode='lines', name='EMA50', line=dict(color='orange')))
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], mode='lines', name='EMA200', line=dict(color='green')))
            fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], mode='lines', name='BB Upper', line=dict(color='gray', dash='dot')))
            fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], mode='lines', name='BB Lower', line=dict(color='gray', dash='dot')))

            # Layout improvements
            fig.update_layout(
                xaxis_rangeslider_visible=False,
                title=f"{pair} {timeframe} Candlestick Chart with Indicators",
                yaxis_title="Price",
                xaxis_title="Date",
                template="plotly_dark",
                height=700
            )

            st.plotly_chart(fig, use_container_width=True)
