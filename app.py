# app.py
import streamlit as st
import pandas as pd
import yfinance as yf
import ta

st.set_page_config(page_title="AI Trading App", layout="wide")

# ----------------------
# Risk Management Function
# ----------------------
def calculate_risk_levels(df, entry_price, risk_ratio=2):
    atr = ta.volatility.AverageTrueRange(
        high=df['High'], 
        low=df['Low'], 
        close=df['Close'], 
        window=14
    ).average_true_range().iloc[-1]

    stop_loss = entry_price - atr
    take_profit = entry_price + (atr * risk_ratio)
    return round(stop_loss, 5), round(take_profit, 5)

# ----------------------
# Signal Generator
# ----------------------
def generate_signal(df):
    df['SMA_20'] = ta.trend.sma_indicator(df['Close'], window=20)
    df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)

    if df['SMA_20'].iloc[-1] > df['SMA_50'].iloc[-1]:
        return "BUY"
    elif df['SMA_20'].iloc[-1] < df['SMA_50'].iloc[-1]:
        return "SELL"
    else:
        return "HOLD"

# ----------------------
# Streamlit UI
# ----------------------
st.title("📈 AI Trading App (Minimal Version)")

symbol = st.text_input("Enter Symbol (e.g., EURUSD=X, BTC-USD, AAPL):", "EURUSD=X")
risk_ratio = st.slider("Risk-Reward Ratio", 1.0, 5.0, 2.0)

if st.button("Get Signal"):
    df = yf.download(symbol, period="1mo", interval="1h")

    if not df.empty:
        signal = generate_signal(df)
        entry_price = df['Close'].iloc[-1]
        sl, tp = calculate_risk_levels(df, entry_price, risk_ratio)

        st.subheader(f"Signal for {symbol}: {signal}")
        st.write(f"Entry Price: {entry_price}")
        st.write(f"Stop Loss: {sl}")
        st.write(f"Take Profit: {tp}")
    else:
        st.error("No data found for the given symbol.")

# ----------------------
# Backtesting (Simple)
# ----------------------
st.subheader("Backtest Example (SMA Crossover)")
if st.button("Run Backtest"):
    df = yf.download(symbol, period="6mo", interval="1h")
    df['Signal'] = 0
    df['SMA_20'] = ta.trend.sma_indicator(df['Close'], window=20)
    df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
    df.loc[df['SMA_20'] > df['SMA_50'], 'Signal'] = 1
    df.loc[df['SMA_20'] < df['SMA_50'], 'Signal'] = -1
    df['Returns'] = df['Close'].pct_change() * df['Signal'].shift(1)
    total_return = (df['Returns'] + 1).prod() - 1
    st.write(f"Total Backtest Return: {total_return:.2%}")
