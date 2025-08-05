import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import plotly.graph_objects as go

st.set_page_config(page_title="Multi-Forex Signal Dashboard", layout="wide")

# -----------------------------
# Sidebar Configuration
# -----------------------------
st.sidebar.title("Forex Multi-Pair Scanner")

pairs = st.sidebar.multiselect(
    "Select Currency Pairs:",
    ["EURUSD=X","GBPUSD=X","USDJPY=X","AUDUSD=X","USDCAD=X","XAUUSD=X"],
    default=["EURUSD=X","GBPUSD=X","USDJPY=X"]
)

period = st.sidebar.selectbox("Data Period:", ["1d","5d","1mo","3mo"], index=0)
interval = st.sidebar.selectbox("Candle Interval:", ["15m","30m","1h","4h","1d"], index=2)
st.sidebar.info("Signals use RSI+MACD+EMA | SL 20 pips | TP 40 pips")

# -----------------------------
# Helper Functions
# -----------------------------
@st.cache_data
def get_data(pair, period, interval):
    df = yf.download(pair, period=period, interval=interval)
    df.dropna(inplace=True)
    return df

def generate_signals(df):
    # Ensure Close is 1D
    close_price = df['Close']
    if isinstance(close_price, pd.DataFrame):
        close_price = close_price.iloc[:,0]

    # Indicators
    df['RSI'] = ta.momentum.RSIIndicator(close_price, window=14).rsi()
    macd = ta.trend.MACD(close_price)
    df['MACD'] = macd.macd()
    df['Signal_Line'] = macd.macd_signal()
    df['EMA50'] = ta.trend.EMAIndicator(close_price, window=50).ema_indicator()
    df['EMA200'] = ta.trend.EMAIndicator(close_price, window=200).ema_indicator()

    # Generate Signals
    signals = []
    for i in range(1, len(df)):
        if df['RSI'][i] < 30 and df['EMA50'][i] > df['EMA200'][i] and df['MACD'][i] > df['Signal_Line'][i]:
            signals.append("BUY")
        elif df['RSI'][i] > 70 and df['EMA50'][i] < df['EMA200'][i] and df['MACD'][i] < df['Signal_Line'][i]:
            signals.append("SELL")
        else:
            signals.append("HOLD")
    signals.insert(0,"HOLD")
    df['Signal'] = signals

    # Stop Loss and Take Profit (vectorized, safe for Cloud)
    df['Stop_Loss'] = None
    df['Take_Profit'] = None

    df.loc[df['Signal']=="BUY", 'Stop_Loss'] = df['Close']*0.998
    df.loc[df['Signal']=="BUY", 'Take_Profit'] = df['Close']*1.004

    df.loc[df['Signal']=="SELL", 'Stop_Loss'] = df['Close']*1.002
    df.loc[df['Signal']=="SELL", 'Take_Profit'] = df['Close']*0.996

    # Trade result simulation for accuracy
    trade_results = []
    for i in range(len(df)):
        if df['Signal'][i] in ['BUY','SELL']:
            if df['Signal'][i] == 'BUY':
                if df['High'][i:].max() >= df['Take_Profit'][i]:
                    trade_results.append("Win")
                elif df['Low'][i:].min() <= df['Stop_Loss'][i]:
                    trade_results.append("Loss")
                else:
                    trade_results.append("Open")
            else:
                if df['Low'][i:].min() <= df['Take_Profit'][i]:
                    trade_results.append("Win")
                elif df['High'][i:].max() >= df['Stop_Loss'][i]:
                    trade_results.append("Loss")
                else:
                    trade_results.append("Open")
        else:
            trade_results.append(None)
    df['Result'] = trade_results
    accuracy = round((df['Result'].value_counts().get('Win',0) / 
                      max(1,len(df[df['Signal'].isin(['BUY','SELL'])]))) * 100,2)

    return df, accuracy

# -----------------------------
# Multi-Pair Scan Summary
# -----------------------------
signal_summary = []
for pair in pairs:
    df = get_data(pair, period, interval)
    if df.empty:
        signal_summary.append([pair, "No Data", "-", "-"])
        continue
    df, acc = generate_signals(df)
    latest_signal = df['Signal'].iloc[-1]
    latest_price = round(df['Close'].iloc[-1],5)
    signal_summary.append([pair, latest_signal, latest_price, acc])

summary_df = pd.DataFrame(signal_summary, columns=["Pair","Signal","Last Price","Accuracy %"])

st.title("📊 Multi-Forex Signal Dashboard")
st.dataframe(summary_df, use_container_width=True)

# -----------------------------
# Detailed View
# -----------------------------
st.subheader("Detailed Pair Analysis")
selected_pair = st.selectbox("Select a pair for chart & history:", pairs)

df = get_data(selected_pair, period, interval)
if not df.empty:
    df, acc = generate_signals(df)

    # Candlestick with signals
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name='Candles'
    ))
    buy_signals = df[df['Signal']=="BUY"]
    sell_signals = df[df['Signal']=="SELL"]
    fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['Close'], mode='markers', marker=dict(color='green', size=10), name='Buy'))
    fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['Close'], mode='markers', marker=dict(color='red', size=10), name='Sell'))
    fig.update_layout(height=600, xaxis_rangeslider_visible=False)

    st.plotly_chart(fig, use_container_width=True)
    st.write("Recent Trade History")
    st.dataframe(df[['Close','RSI','MACD','Signal','Result']].tail(20))
else:
    st.warning(f"No data available for {selected_pair} at the selected interval.")
