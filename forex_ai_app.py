import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import ta
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timedelta

# Page setup
st.set_page_config(page_title="Forex AI Signals", layout="wide")

st.title("💹 Flexible & Accurate Forex AI Signal App")

# Sidebar settings
st.sidebar.header("Settings")
pair = st.sidebar.selectbox("Currency Pair", [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X",
    "AUDUSD=X", "USDCAD=X", "NZDUSD=X", "USDCHF=X"
], index=0)

period = st.sidebar.selectbox("Period", ["1d", "5d", "1mo"], index=0)
interval = st.sidebar.selectbox("Interval", ["1m", "5m", "15m", "30m", "1h"], index=1)
refresh_rate = st.sidebar.slider("Auto-refresh (seconds)", 30, 300, 60)

# --- Flexible Strategy Parameters ---
st.sidebar.subheader("Strategy Settings")
ma_length = st.sidebar.slider("Moving Average Length", 5, 100, 20)
rsi_buy = st.sidebar.slider("RSI Buy Threshold", 10, 50, 30)
rsi_sell = st.sidebar.slider("RSI Sell Threshold", 50, 90, 70)

# Auto-refresh
st_autorefresh(interval=refresh_rate * 1000, key="forexrefresh")

st.info(f"Fetching {pair} | Period: {period} | Interval: {interval} | Refresh: {refresh_rate}s")

# --- Download forex data ---
data = yf.download(pair, period=period, interval=interval)

if data.empty:
    st.error("⚠️ No data returned! Try another interval or currency pair.")
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

# Ensure numeric and drop missing values
data['Close'] = pd.to_numeric(data['Close'], errors='coerce')
data = data.dropna(subset=['Close'])

# --- Calculate Indicators ---
data['MA'] = data['Close'].rolling(window=ma_length).mean()
data['RSI'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
macd = ta.trend.MACD(data['Close'])
data['MACD'] = macd.macd()
data['MACD_Signal'] = macd.macd_signal()
data = data.dropna()

# --- Generate Smarter Signals ---
def signal_with_confidence(row):
    conditions = []
    # Basic MA + RSI
    if row['Close'] > row['MA'] and row['RSI'] < rsi_buy:
        conditions.append('BUY')
    elif row['Close'] < row['MA'] and row['RSI'] > rsi_sell:
        conditions.append('SELL')
    
    # MACD Confirmation
    if row['MACD'] > row['MACD_Signal']:
        conditions.append('MACD_BUY')
    elif row['MACD'] < row['MACD_Signal']:
        conditions.append('MACD_SELL')
    
    # Combine into a single signal with confidence
    if 'BUY' in conditions and 'MACD_BUY' in conditions:
        return 'BUY', 100
    elif 'BUY' in conditions:
        return 'BUY', 60
    elif 'SELL' in conditions and 'MACD_SELL' in conditions:
        return 'SELL', 100
    elif 'SELL' in conditions:
        return 'SELL', 60
    else:
        return 'HOLD', 20

data[['Signal', 'Confidence']] = data.apply(lambda row: pd.Series(signal_with_confidence(row)), axis=1)

# --- Display Latest Signals ---
st.subheader("📊 Latest Signals")
st.write(data[['Datetime', 'Close', 'MA', 'RSI', 'MACD', 'Signal', 'Confidence']].tail(15))

# --- Count Weekly Signals ---
last_week = datetime.now() - timedelta(days=7)
recent_signals = data[data['Datetime'] >= last_week]
signal_counts = recent_signals['Signal'].value_counts()

st.subheader("📈 Signal Frequency (Last 7 Days)")
st.write(signal_counts)
st.bar_chart(signal_counts)

# --- Plot Price with MA ---
fig, ax1 = plt.subplots(figsize=(12,5))
ax1.plot(data['Datetime'], data['Close'], label='Close Price', color='blue')
ax1.plot(data['Datetime'], data['MA'], label=f'MA{ma_length}', color='orange')
ax1.set_title(f'{pair} Price & {ma_length}-period Moving Average')
ax1.legend()
st.pyplot(fig)

# --- Plot RSI ---
fig, ax2 = plt.subplots(figsize=(12,3))
ax2.plot(data['Datetime'], data['RSI'], color='purple', label='RSI')
ax2.axhline(rsi_sell, color='red', linestyle='--')
ax2.axhline(rsi_buy, color='green', linestyle='--')
ax2.set_title(f'{pair} RSI')
ax2.legend()
st.pyplot(fig)

# --- Plot MACD ---
fig, ax3 = plt.subplots(figsize=(12,3))
ax3.plot(data['Datetime'], data['MACD'], label='MACD', color='cyan')
ax3.plot(data['Datetime'], data['MACD_Signal'], label='Signal', color='orange')
ax3.axhline(0, color='black', linestyle='--')
ax3.set_title(f'{pair} MACD')
ax3.legend()
st.pyplot(fig)

st.caption("Flexible & Accurate AI Forex Signals | Weekly Stats Included | Data source: Yahoo Finance")
