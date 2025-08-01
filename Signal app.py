import streamlit as st
import backtrader as bt
from datetime import datetime
import pandas as pd
from strategies import SMACrossover, RSIStrategy

# App Configuration
st.set_page_config(layout="wide")
st.title("📊 Mobile Forex Strategy Analyzer")

# Sidebar Controls
with st.sidebar:
    st.header("Strategy Parameters")
    pair = st.selectbox("Currency Pair", ["EURUSD=X", "GBPUSD=X", "USDJPY=X"])
    timeframe = st.selectbox("Timeframe", ["Daily", "Hourly"])
    strategy = st.selectbox("Strategy", ["SMA Crossover", "RSI", "MACD"])
    
    if strategy == "SMA Crossover":
        fast = st.slider("Fast SMA Period", 5, 50, 10)
        slow = st.slider("Slow SMA Period", 20, 100, 30)
    elif strategy == "RSI":
        rsi_period = st.slider("RSI Period", 5, 30, 14)
        rsi_low = st.slider("Buy Below RSI", 10, 40, 30)
        rsi_high = st.slider("Sell Above RSI", 60, 90, 70)

# Backtest Execution
if st.button("Run Backtest"):
    st.write("Loading data...")
    
    # Get data
    data = bt.feeds.YahooFinanceData(
        dataname=pair,
        fromdate=datetime(2023,1,1),
        todate=datetime(2023,12,31),
        timeframe=bt.TimeFrame.Days if timeframe == "Daily" else bt.TimeFrame.Minutes
    )
    
    # Initialize Cerebro Engine
    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    
    # Add selected strategy
    if strategy == "SMA Crossover":
        cerebro.addstrategy(SMACrossover, fast=fast, slow=slow)
    elif strategy == "RSI":
        cerebro.addstrategy(RSIStrategy, period=rsi_period, rsi_low=rsi_low, rsi_high=rsi_high)
    
    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    
    # Run backtest
    results = cerebro.run()
    strat = results[0]
    
    # Display results
    st.success(f"Final Portfolio Value: ${cerebro.broker.getvalue():.2f}")
    st.write(f"Sharpe Ratio: {strat.analyzers.sharpe.get_analysis()['sharperatio']:.2f}")
    st.write(f"Max Drawdown: {strat.analyzers.drawdown.get_analysis()['max']['drawdown']:.2f}%")
