import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.set_page_config(page_title="Forex Strategy Backtester", layout="wide")
st.title("📊 Forex Strategy Backtester & Optimizer")

# --- Sidebar Inputs ---
st.sidebar.header("Settings")
pair = st.sidebar.selectbox("Currency Pair", [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X",
    "AUDUSD=X", "USDCAD=X", "NZDUSD=X", "USDCHF=X"
], index=0)

interval = st.sidebar.selectbox("Interval", ["1h", "4h", "1d"], index=0)
st.sidebar.write("We'll analyze **up to 1 year** of data for this pair.")

# --- Download Data Function (no datetime module) ---
def download_forex_data(symbol, interval):
    """Download up to 1 year of data, handling intraday 60-day limit."""
    if interval == "1d":
        return yf.download(symbol, period="1y", interval=interval)
    else:
        # Intraday: Stitch together 6×60-day periods using pandas dates
        combined_df = pd.DataFrame()
        end_date = pd.Timestamp.today().normalize()

        for i in range(6):  # 6 segments ≈ 1 year
            segment_end = end_date - pd.Timedelta(days=i*60)
            segment_start = segment_end - pd.Timedelta(days=60)
            df = yf.download(symbol, 
                             start=segment_start.strftime("%Y-%m-%d"), 
                             end=segment_end.strftime("%Y-%m-%d"), 
                             interval=interval)
            combined_df = pd.concat([df, combined_df])

        return combined_df.drop_duplicates()

# --- Load Data ---
data = download_forex_data(pair, interval)

if data.empty:
    st.error("⚠️ No data returned! Try another interval or currency pair.")
    st.stop()

data = data.reset_index()
data['Close'] = pd.to_numeric(data['Close'], errors='coerce')
data.dropna(inplace=True)

# --- Backtest Function ---
def backtest_strategy(df, ma_length=20, rsi_buy=30, rsi_sell=70):
    df['MA'] = df['Close'].rolling(window=ma_length).mean()
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()

    balance = 1000  # starting capital
    position = 0
    entry_price = 0

    for i in range(len(df)):
        close = df['Close'].iloc[i]
        rsi = df['RSI'].iloc[i]
        ma = df['MA'].iloc[i]

        # Buy condition
        if position == 0 and close > ma and rsi < rsi_buy:
            position = 1
            entry_price = close

        # Sell condition
        elif position == 1 and close < ma and rsi > rsi_sell:
            balance *= close / entry_price
            position = 0

    # Close any open trade at the end
    if position == 1:
        balance *= df['Close'].iloc[-1] / entry_price

    return balance

# --- Optimization ---
st.subheader("🔍 Optimizing Strategy... This may take a moment")
best_balance = 0
best_params = None

for ma in [10, 20, 50]:
    for rsi_b in [25, 30, 35]:
        for rsi_s in [65, 70, 75]:
            final_balance = backtest_strategy(data.copy(), ma, rsi_b, rsi_s)
            if final_balance > best_balance:
                best_balance = final_balance
                best_params = (ma, rsi_b, rsi_s)

st.success(f"✅ Best Strategy Found: MA={best_params[0]}, RSI Buy={best_params[1]}, RSI Sell={best_params[2]}")
st.write(f"💰 Final Balance after 1 year: ${round(best_balance,2)} (starting with $1000)")

st.line_chart(data[['Close']])
st.caption("Backtest based on MA+RSI strategy | Data source: Yahoo Finance")
