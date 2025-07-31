import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import ta

st.title("💹 Forex AI Signal App")

# Sidebar settings
st.sidebar.header("Settings")
pair = st.sidebar.text_input("Currency Pair", "EURUSD=X")
period = st.sidebar.selectbox("Period", ["1mo", "3mo", "6mo", "1y"], index=0)
interval = st.sidebar.selectbox("Interval", ["30m", "1h", "2h", "4h"], index=1)

st.write(f"Fetching data for: {pair}")

# --- Download latest forex data ---
data = yf.download(pair, period=period, interval=interval)
data = data.reset_index()

# --- Fix MultiIndex issue on Streamlit Cloud ---
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(-1)

# --- Ensure 'Close' is numeric ---
data['Close'] = pd.to_numeric(data['Close'], errors='coerce')

# --- Calculate Indicators ---
data['MA50'] = data['Close'].rolling(window=50).mean()
data['RSI'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
data = data.dropna()

# --- Generate Trading Signals ---
def smarter_signal(row):
    if row['Close'] > row['MA50'] and row['RSI'] < 30:
        return 'BUY'
    elif row['Close'] < row['MA50'] and row['RSI'] > 70:
        return 'SELL'
    else:
        return 'HOLD'

data['Signal'] = data.apply(smarter_signal, axis=1)

# --- Display Latest Signals ---
st.subheader("📊 Latest Signals")
st.write(data[['Datetime', 'Close', 'MA50', 'RSI', 'Signal']].tail(10))

# --- Plot Price with MA50 ---
fig, ax1 = plt.subplots(figsize=(12,5))
ax1.plot(data['Datetime'], data['Close'], label='Close Price', color='blue')
ax1.plot(data['Datetime'], data['MA50'], label='MA50', color='orange')
ax1.set_title(f'{pair} Price & 50-period Moving Average')
ax1.legend()
st.pyplot(fig)

# --- Plot RSI ---
fig, ax2 = plt.subplots(figsize=(12,3))
ax2.plot(data['Datetime'], data['RSI'], color='purple', label='RSI')
ax2.axhline(70, color='red', linestyle='--')
ax2.axhline(30, color='green', linestyle='--')
ax2.set_title(f'{pair} RSI')
ax2.legend()
st.pyplot(fig)
