import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import strategy

st.set_page_config(page_title="Trading Signal App", layout="wide")

st.title("Trading Signal App with MACD, RSI & Bollinger Bands")

ticker = st.text_input("Enter ticker symbol (e.g. AAPL, TSLA, MSFT):", value="AAPL")
period = st.selectbox("Select data period:", ['1mo', '3mo', '6mo', '1y', '2y', '5y', '10y'], index=3)

if ticker:
    with st.spinner(f"Downloading data for {ticker}..."):
        df = yf.download(ticker, period=period, progress=False)

    if df.empty:
        st.error("No data found for this ticker.")
    else:
        # Calculate indicators first
        df = strategy.calculate_indicators(df)

        # Show columns to debug if needed
        st.write("Columns after indicator calculation:", df.columns.tolist())

        # Generate signals after indicator calculation
        try:
            df = strategy.generate_signals(df)
        except KeyError as e:
            st.error(f"Error generating signals: {e}")
            st.stop()

        st.subheader("Historical Price with Signals")

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df.index, df['Close'], label='Close Price', color='blue')
        ax.plot(df.index, df['Upper_BB'], label='Upper BB', linestyle='--', color='gray')
        ax.plot(df.index, df['Lower_BB'], label='Lower BB', linestyle='--', color='gray')

        buy_signals = df[df['Signal'] == 1]
        sell_signals = df[df['Signal'] == -1]

        ax.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='green', s=100, label='Buy Signal')
        ax.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='red', s=100, label='Sell Signal')

        ax.set_title(f"{ticker} Close Price & Trading Signals")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.legend()
        st.pyplot(fig)

        st.subheader("Strategy Performance")

        stats = strategy.backtest_signals(df)
        st.write(f"Total Trades: {stats['total_trades']}")
        st.write(f"Win Rate: {stats['win_rate']*100:.2f}%")
        st.write(f"Total Return: {stats['total_return']*100:.2f}%")

        st.subheader("Latest Signal")
        latest = df.iloc[-1]
        signal_text = "Hold"
        if latest['Signal'] == 1:
            signal_text = "Buy"
        elif latest['Signal'] == -1:
            signal_text = "Sell"
        st.write(f"Latest Signal for {ticker}: **{signal_text}**")
