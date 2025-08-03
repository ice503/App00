import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from indicators import calculate_indicators
from signal_engine import generate_signal
from openai import OpenAI

# --- Streamlit page setup ---
st.set_page_config(page_title="AI Forex Signal App", layout="wide")
st.title("📊 AI-Powered Forex Signal & Strategy App")

# --- API Setup ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])  # Add key in Streamlit secrets

# --- Initialize strategy parameters ---
if "strategy_params" not in st.session_state:
    st.session_state.strategy_params = {
        "rsi_buy_threshold": 50,
        "rsi_sell_threshold": 50,
        "atr_multiplier": 1.5
    }

# --- User Inputs for chart ---
symbol = st.selectbox("Select Pair", ["EURUSD=X", "GBPUSD=X", "BTC-USD"])
timeframe = st.selectbox("Timeframe", ["1h", "4h", "1d"])
days = st.slider("History (days)", 7, 60, 30)

# --- Fetch Data ---
data = yf.download(symbol, period=f"{days}d", interval=timeframe)
if data.empty:
    st.error("⚠ No data fetched. Try again later.")
else:
    # --- Compute indicators ---
    df = calculate_indicators(data)
    
    # --- Plot candlestick with EMAs ---
    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']
    )])
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='blue'), name='EMA20'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], line=dict(color='orange'), name='EMA50'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], line=dict(color='red'), name='EMA200'))
    st.plotly_chart(fig, use_container_width=True)

    # --- Show latest signal with current strategy params ---
    st.subheader("📈 Latest Signal Recommendation")
    signal_info = generate_signal(df, st.session_state.strategy_params)
    st.write(signal_info)

# --- AI Chat Section ---
st.subheader("🤖 AI Trading Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are an expert Forex trading assistant. You explain signals and suggest adjustments."}
    ]

# Display past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask me about the strategy or adjust settings..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=st.session_state.messages
    )
    reply = response.choices[0].message["content"]

    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

    # --- Optional: Detect strategy adjustment commands ---
    if "increase atr" in prompt.lower():
        st.session_state.strategy_params["atr_multiplier"] += 0.5
        st.success(f"ATR Multiplier increased to {st.session_state.strategy_params['atr_multiplier']}x")
    elif "decrease atr" in prompt.lower():
        st.session_state.strategy_params["atr_multiplier"] = max(0.5, st.session_state.strategy_params["atr_multiplier"] - 0.5)
        st.success(f"ATR Multiplier decreased to {st.session_state.strategy_params['atr_multiplier']}x")
    elif "rsi buy" in prompt.lower():
        import re
        match = re.search(r"(\d+)", prompt)
        if match:
            st.session_state.strategy_params["rsi_buy_threshold"] = int(match.group(1))
            st.success(f"RSI Buy Threshold updated to {match.group(1)}")
    elif "rsi sell" in prompt.lower():
        import re
        match = re.search(r"(\d+)", prompt)
        if match:
            st.session_state.strategy_params["rsi_sell_threshold"] = int(match.group(1))
            st.success(f"RSI Sell Threshold updated to {match.group(1)}")
