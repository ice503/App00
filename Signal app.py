import streamlit as st
import backtrader as bt
import yfinance as yf
import pandas as pd
from datetime import datetime
from strategies import SMACrossover, RSIStrategy
import pytz

# Configure app
st.set_page_config(layout="wide")
st.title("📊 Forex Strategy Analyzer")

# --- Data Loading with Caching ---
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_data(pair="EURUSD=X", year=2023, timeframe="Daily"):
    """Load data using yfinance with error handling"""
    try:
        # Download data
        df = yf.download(
            pair,
            start=f"{year}-01-01",
            end=f"{year}-12-31",
            interval="1h" if timeframe == "Hourly" else "1d"
        )
        
        # Clean data
        df.index = df.index.tz_localize(None)  # Remove timezone
        df.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }, inplace=True)
        
        # Convert to backtrader format
        data = bt.feeds.PandasData(dataname=df)
        return data
        
    except Exception as e:
        st.error(f"❌ Failed to load data: {str(e)}")
        return None

# --- UI Controls ---
with st.sidebar:
    st.header("Parameters")
    
    # Input controls
    pair = st.selectbox("Currency Pair", ["EURUSD=X", "GBPUSD=X", "USDJPY=X"])
    year = st.number_input("Year", 2020, 2023, 2023)
    timeframe = st.selectbox("Timeframe", ["Daily", "Hourly"])
    strategy = st.selectbox("Strategy", ["SMA Crossover", "RSI"])
    
    # Strategy-specific parameters
    if strategy == "SMA Crossover":
        fast = st.slider("Fast SMA", 5, 50, 10)
        slow = st.slider("Slow SMA", 20, 100, 30)
    else:
        rsi_period = st.slider("RSI Period", 5, 30, 14)
        rsi_low = st.slider("Buy Below RSI", 10, 40, 30)
        rsi_high = st.slider("Sell Above RSI", 60, 90, 70)

# --- Backtest Execution ---
if st.button("💡 Run Analysis"):
    with st.spinner("Running backtest..."):
        # Load data
        data = get_data(pair, year, timeframe)
        if data is None:
            st.stop()
        
        # Configure Cerebro
        cerebro = bt.Cerebro()
        cerebro.adddata(data)
        
        # Add strategy
        if strategy == "SMA Crossover":
            cerebro.addstrategy(SMACrossover, fast=fast, slow=slow)
        else:
            cerebro.addstrategy(RSIStrategy, 
                              period=rsi_period, 
                              rsi_low=rsi_low, 
                              rsi_high=rsi_high)
        
        # Add analyzers
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        
        # Run backtest
        try:
            results = cerebro.run()
            strat = results[0]
            
            # Display results
            st.success("✅ Backtest Completed")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Final Value", f"${cerebro.broker.getvalue():.2f}")
                st.metric("Sharpe Ratio", 
                         f"{strat.analyzers.sharpe.get_analysis()['sharperatio']:.2f}")
                
            with col2:
                st.metric("Max Drawdown", 
                         f"{strat.analyzers.drawdown.get_analysis()['max']['drawdown']:.2f}%")
                
                trades = strat.analyzers.trades.get_analysis()
                win_rate = trades.won.total / trades.total.closed * 100
                st.metric("Win Rate", f"{win_rate:.1f}%")
                
        except Exception as e:
            st.error(f"Backtest failed: {str(e)}")
