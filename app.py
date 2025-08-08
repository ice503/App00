import streamlit as st
import pandas as pd
import yfinance as yf
import ta

def get_data(symbol, period="3mo", interval="1d"):
    df = yf.download(symbol, period=period, interval=interval)

    # Flatten multi-index columns if exist
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [' '.join(col).strip() for col in df.columns.values]

    df = df.reset_index()

    wanted_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    existing_cols = [col for col in wanted_cols if col in df.columns]
    df = df[existing_cols]

    return df

def generate_signal(df):
    if df.empty:
        return "No data"

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
