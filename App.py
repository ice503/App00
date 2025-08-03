import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import requests
import time
from indicators import calculate_indicators
from signal_engine import generate_signal

# --------------------------
# Streamlit Page Setup
# --------------------------
st.set_page_config(page_title="AI Forex Signal App", layout="wide")
st.title("📊 AI Forex Signal & Strategy Assistant (Free Hugging Face Version)")

# --------------------------
# Hugging Face AI Function
# --------------------------
def ask_ai(prompt, retries=2):
    """
    Use Hugging Face free model with automatic retry if model is cold.
    """
    hf_token = st.secrets.get("HF_TOKEN", "")
    headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}
    payload = {
        "inputs": f"You are a professional Forex trading assistant. {prompt}",
        "parameters": {"max_new_tokens": 200, "temperature": 0.7}
    }

    for attempt in range(retries):
        try:
            response = requests.post(
                "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
                headers=headers,
                json=payload,
                timeout=30
            )

            # Hugging Face returns JSON or plain text
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and "generated_text" in result[0]:
                    return result[0]["generated_text"]
                else:
                    return f"⚠ AI response format issue: {result}"
            else:
                st.warning(f"Hugging Face status {response.status_code}, retrying...")
                time.sleep(5)  # Wait before retry

        except Exception as e:
            st.warning(f"Hugging Face request failed: {e}, retrying...")
            time.sleep(5)

    return "⚠ AI is currently unavailable. Try again in 1-2 minutes."

# --------------------------
# Strategy Parameters
# --------------------------
if "strategy_params" not in st.session_state:
    st.session_state.strategy_params = {
        "rsi_buy_threshold": 50,
        "rsi_sell_threshold": 50,
        "atr_multiplier": 1.5
    }

# --------------------------
# User Inputs
# --------------------------
symbol = st.selectbox("Select Pair", ["EURUSD=X", "GBPUSD=X", "BTC-USD"])
timeframe = st.selectbox("Timeframe", ["1h", "4h", "1d"])
days = st.slider("History (days)", 7, 60, 30)

# --------------------------
# Fetch Market Data
# --------------------------
data = yf.download(symbol, period=f"{days}d", interval=timeframe)
if data.empty:
    st.error("⚠ No data fetched. Try again later.")
else:
    # Calculate Indicators
    df = calculate_indicators(data)

    # --------------------------
    # Plot Candlestick + EMAs
    # --------------------------
    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close']
    )])
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], line=dict(color='blue'), name='EMA20'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], line=dict(color='orange'), name='EMA50'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], line=dict(color='red'), name='EMA200'))
    st.plotly_chart(fig, use_container_width=True)

    # --------------------------
    # Generate Signal
    # --------------------------
    st.subheader("📈 Latest Signal Recommendation")
    signal_info = generate_signal(df, st.session_state.strategy_params)
    st.write(signal_info)

# --------------------------
# AI Chat Assistant
# --------------------------
st.subheader("🤖 AI Trading Assistant (Free)")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle user input for AI
if prompt := st.chat_input("Ask about signals or change settings..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI reply
    reply = ask_ai(prompt)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

    # --------------------------
    # Simple Command Recognition
    # --------------------------
    if "increase atr" in prompt.lower():
        st.session_state.strategy_params["atr_multiplier"] += 0.5
        st.success(f"ATR Multiplier increased to {st.session_state.strategy_params['atr_multiplier']}x")
    elif "decrease atr" in prompt.lower():
        st.session_state.strategy_params["atr_multiplier"] = max(
            0.5, st.session_state.strategy_params["atr_multiplier"] - 0.5
        )
        st.success(f"ATR Multiplier decreased to {st.session_state.strategy_params['atr_multiplier']}x")
