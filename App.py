import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def calculate_indicators(df):
    df = df.copy()
    # EMAs
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()
    
    # Bollinger Bands
    sma20 = df['Close'].rolling(window=20).mean()
    std20 = df['Close'].rolling(window=20).std()
    df['BB_upper'] = sma20 + (std20 * 2)
    df['BB_lower'] = sma20 - (std20 * 2)
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_hist'] = df['MACD'] - df['MACD_signal']
    
    return df.dropna()

def main():
    st.set_page_config(page_title="Live Trading Chart", layout="wide")
    st.title("📈 Live Candlestick Chart with Indicators")

    symbol = st.text_input("Enter ticker symbol", value="EURUSD=X")
    timeframe = st.selectbox("Select timeframe", ["1h", "4h", "1d"], index=0)
    period = st.selectbox("Select period", ["1mo", "3mo", "6mo"], index=0)

    st.write(f"Loading data for **{symbol}**, timeframe: **{timeframe}**, period: **{period}**")

    data = yf.download(symbol, period=period, interval=timeframe)
    if data.empty:
        st.error("No data found. Please check the symbol and try again.")
        return

    df = calculate_indicators(data)

    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        row_heights=[0.6, 0.2, 0.2],
        vertical_spacing=0.05,
        subplot_titles=("Price + EMAs + Bollinger Bands", "MACD", "RSI")
    )

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='Candlestick',
        increasing_line_color='green', decreasing_line_color='red',
        showlegend=False
    ), row=1, col=1)

    # EMAs
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], mode='lines', line=dict(color='yellow', width=1), name='EMA20'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], mode='lines', line=dict(color='orange', width=1), name='EMA50'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], mode='lines', line=dict(color='blue', width=2), name='EMA200'), row=1, col=1)

    # Bollinger Bands
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], mode='lines', line=dict(color='lightblue', width=1, dash='dot'), name='BB Upper'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], mode='lines', line=dict(color='lightblue', width=1, dash='dot'), name='BB Lower'), row=1, col=1)

    # MACD
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], mode='lines', line=dict(color='cyan', width=1), name='MACD'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD_signal'], mode='lines', line=dict(color='magenta', width=1), name='Signal'), row=2, col=1)
    fig.add_bar(x=df.index, y=df['MACD_hist'], name='Histogram', marker_color='grey', opacity=0.5, row=2, col=1)

    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], mode='lines', line=dict(color='white', width=1), name='RSI'), row=3, col=1)
    fig.add_hline(y=70, line_dash="dot", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="green", row=3, col=1)

    fig.update_layout(
        template='plotly_dark',
        height=900,
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )

    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
