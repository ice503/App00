import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import ta

# --- Auto-refresh every 60 seconds ---
st.set_page_config(page_title="Forex AI Signals", layout="wide")
st_autorefresh = st.experimental_rerun  # Fallback for future-proofing

st.title("💹 Live Forex AI Signal App")

# Sidebar settings
st.sidebar.header("Settings")
pair = st.sidebar.selectbox("Currency Pair", [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X",
    "AUDUSD=X", "USDCAD=X", "NZDUSD=X", "USDCHF=X"
], index=0)

period = st.sidebar.selectbox("Period", ["1d", "5d", "1mo"], index=0)
interval = st.sidebar.selectbox("Interval", ["1m", "5m", "15m", "30m", "1h"], index=1)

refresh_rate = st.sidebar.slider("Auto-refresh (seconds)", 30, 300, 60)

st.info(f"Fetching {pair} data | Period: {period} | Interval: {interval} | Refresh every {refresh_rate}s")

# --- Auto-refresh ---
st.experimental_set_query_params(refresh=str(refresh_rate))

# --- Download forex data ---
data = yf.download(pair, period=period, interval=interval)

if data.empty:
    st.error("⚠️ No data returned! Try a different interval or currency pair.")
    st.stop()

data = data.reset_index()

# --- Fix MultiIndex columns ---
if isinstance(data.columns, pd.MultiIndex):
    data.columns = [c[0] if c[0] != '' else c[1] for c in data.columns]

# --- Detect Close column ---
close_col = None
for col in data.columns:
    if col.lower() == 'close':
        close_col = col
        break

if close_col is None:
    for col in data.columns[1:]:
        if pd.api.types.is_numeric_dtype(data[col]):
            close_col = col
            break

if close_col is None:
    st.error(f"⚠️ Could not identify Close column. Columns: {list(data.columns)}")
    st.stop()

# Rename Close column if needed
if close_col != 'Close':
    data.rename(columns={close_col: 'Close'}, inplace=True)

# Ensure numeric
data['Close'] = pd.to_numeric(data['Close'], errors='coerce')
data = data.dropna(subset=['Close'])

# --- Calculate Indicators ---
data['MA20'] = data['Close'].rolling(window=20).mean()
data['RSI'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
data = data.dropna()

# --- Generate Trading Signals ---
def smarter_signal(row):
    if row['Close'] > row['MA20'] and row['RSI'] < 30:
        return 'BUY'
    elif row['Close'] < row['MA20'] and row['RSI'] > 70:
        return 'SELL'
    else:
        return 'HOLD'

data['Signal'] = data.apply(smarter_signal, axis=1)

# --- Display Latest Signals ---
st.subheader("📊 Latest Signals")
st.write(data[['Datetime', 'Close', 'MA20', 'RSI', 'Signal']].tail(15))

# --- Plot Price with MA20 ---
fig, ax1 = plt.subplots(figsize=(12,5))
ax1.plot(data['Datetime'], data['Close'], label='Close Price', color='blue')
ax1.plot(data['Datetime'], data['MA20'], label='MA20', color='orange')
ax1.set_title(f'{pair} Price & 20-period Moving Average')
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

st.caption("Auto-refreshing app for live Forex AI signals. Data source: Yahoo Finance")
