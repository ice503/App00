import streamlit as st
import pandas as pd
import yfinance as yf
import ta

# --------------------------
# Function to download data
# --------------------------
def get_data(symbol, period="3mo", interval="1d"):
    df = yf.download(symbol, period=period, interval=interval)
    df = df.reset_index()
    df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    return df

# --------------------------
# Function to generate trading signal
# --------------------------
def generate_signal(df):
    if df.empty:
        return "No data"

    # Calculate SMA safely
    df['SMA_20'] = pd.Series(
        ta.trend.sma_indicator(close=df['Close'], window=20).values,
        index=df.index
    )

    last_close = df['Close'].iloc[-1]
    last_sma20 = df['SMA_20'].iloc[-1]

    if pd.isna(last_sma20):
        return "Not enough data for SMA calculation"

    if last_close > last_sma20:
        return "BUY 📈"
    elif last_close < last_sma20:
        return "SELL 📉"
    else:
        return "HOLD ⚖️"

# --------------------------
# Streamlit UI
# --------------------------
st.title("📊 Simple Trading Signal App")

symbol = st.text_input("Enter stock/forex symbol (Yahoo Finance format):", "EURUSD=X")
period = st.selectbox("Select period", ["1mo", "3mo", "6mo", "1y"])
interval = st.selectbox("Select interval", ["1d", "1h", "30m", "15m", "5m"])

if st.button("Get Signal"):
    df = get_data(symbol, period, interval)

    if not df.empty:
        st.write(f"Showing data for **{symbol}**")
        st.dataframe(df.tail())

        signal = generate_signal(df)
        st.subheader(f"Trading Signal: {signal}")

        st.line_chart(df[['Close', 'SMA_20']])
    else:
        st.error("No data found. Check symbol or connection.")
