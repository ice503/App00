import streamlit as st
import yfinance as yf
import pandas as pd
from signal_engine import calculate_indicators, generate_signal
import plotly.graph_objects as go

st.set_page_config(page_title="Trading Signal Dashboard", layout="wide")

st.title("📊 Professional Trading Signal Dashboard")

# Choose ticker
pair = st.selectbox("Select currency pair or asset:", 
                    ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X', 'USDCHF=X', 'USDCAD=X'])

# Download data: last 7 days, 1h interval
data = yf.download(pair, period="7d", interval="1h")

st.write("### Raw Data Preview")
st.dataframe(data.head())

st.write("### Data Columns")
st.write(list(data.columns))

# Calculate indicators (handles column renaming internally)
try:
    df = calculate_indicators(data)
except Exception as e:
    st.error(f"Error calculating indicators: {e}")
    st.stop()

# Generate signal
signal_info = generate_signal(df)

# Display signal info
st.write("### Trading Signal")
st.write(signal_info)

# Plot candlestick with indicators
fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=df.index,
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close'],
    name="Price"
))

# Add EMA lines
fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='blue', width=1), name='EMA20'))
fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], line=dict(color='orange', width=1), name='EMA50'))
fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], line=dict(color='green', width=1), name='EMA200'))

# Add Bollinger Bands
fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], line=dict(color='grey', width=1, dash='dash'), name='BB Upper'))
fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], line=dict(color='grey', width=1, dash='dash'), name='BB Lower'))

fig.update_layout(
    title=f"{pair} 1H Chart with Indicators",
    xaxis_title="Date",
    yaxis_title="Price",
    xaxis_rangeslider_visible=False,
    height=700
)

st.plotly_chart(fig, use_container_width=True)
