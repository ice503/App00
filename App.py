import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from indicators import calculate_indicators
from signal_engine import generate_signal
from openai import OpenAI

# Streamlit Page Setup
st.set_page_config(page_title="AI Forex Signal App", layout="wide")
st.title("📊 AI Forex Signal & Strategy Assistant")

# OpenAI API
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Strategy Parameters
if "strategy_params" not in st.session_state:
    st.session_state.strategy_params = {
        "rsi_buy_threshold": 50,
        "rsi_sell_threshold": 50,
        "atr_multiplier": 1.5
    }

# User Inputs
symbol = st.selectbox("Select Pair", ["EURUSD=X", "GBPUSD=X", "BTC-USD"])
timeframe = st.selectbox("Timeframe", ["1h", "4h", "1d"])
days = st.slider("History (days)", 7, 60, 30)

# Download Data
data = yf.download(symbol, period=f"{days}d", interval=timeframe)
if data.empty:
    st.error("⚠ No data fetched. Try again later.")
else:
    # Calculate Indicators
    df = calculate_indicators(data)

    # Plot Candlestick Chart with EMAs
    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close']
    )])
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='blue'), name='EMA20'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], line=dict(color='orange'), name='EMA50'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], line=dict(color='red'), name='EMA200'))
    st.plotly_chart(fig, use_container_width=True)

    # Generate Latest Signal
    st.subheader("📈 Latest Signal Recommendation")
    signal_info = generate_signal(df, st.session_state.strategy_params)
    st.write(signal_info)

# AI Chat Assistant
st.subheader("🤖 AI Trading Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are an expert Forex trading assistant. Explain signals and suggest strategy changes."}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask me about signals or change settings..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=st.session_state.messages
    )
    reply = response.choices[0].message["content"]

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

    # Simple command recognition
    if "increase atr" in prompt.lower():
        st.session_state.strategy_params["atr_multiplier"] += 0.5
        st.success(f"ATR Multiplier increased to {st.session_state.strategy_params['atr_multiplier']}x")
    elif "decrease atr" in prompt.lower():
        st.session_state.strategy_params["atr_multiplier"] = max(0.5, st.session_state.strategy_params["atr_multiplier"] - 0.5)
        st.success(f"ATR Multiplier decreased to {st.session_state.strategy_params['atr_multiplier']}x")
