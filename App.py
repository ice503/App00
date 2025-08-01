import streamlit as st
import backtrader as bt
import yfinance as yf
import pandas as pd
from datetime import datetime
from strategies import SMACrossover, RSIStrategy

# Configure app for mobile
st.set_page_config(
    layout="wide",
    page_title="📱 Forex Strategy Tester",
    initial_sidebar_state="expanded"
)

@st.cache_data(ttl=3600, show_spinner="Loading market data...")
def get_data(pair="EURUSD=X", year=2023, timeframe="Daily"):
    """Safe data loader with validation"""
    try:
        # Download data
        interval = "1h" if timeframe == "Hourly" else "1d"
        df = yf.download(
            pair,
            start=f"{year}-01-01",
            end=f"{year}-12-31",
            interval=interval,
            progress=False,
            repair=True  # Fixes Yahoo Finance gaps
        )
        
        # Validate data
        if len(df) < 30:
            raise ValueError(f"Only {len(df)} rows found")
            
        # Standardize columns
        df = df.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close'
        })[['open','high','low','close']]
        
        # Remove timezone and NaN
        df.index = pd.to_datetime(df.index).tz_localize(None)
        df = df.dropna()
        
        return bt.feeds.PandasData(dataname=df)
        
    except Exception as e:
        st.error(f"❌ Data error: {str(e)}")
        return None

# UI Controls
with st.sidebar:
    st.header("Parameters")
    pair = st.selectbox("Pair", ["EURUSD=X", "GBPUSD=X", "USDJPY=X"])
    year = st.select_slider("Year", [2021, 2022, 2023], 2023)
    timeframe = st.radio("Timeframe", ["Daily", "Hourly"])
    strategy = st.selectbox("Strategy", ["SMA Crossover", "RSI"])
    
    if strategy == "SMA Crossover":
        fast = st.slider("Fast SMA", 5, 20, 10)
        slow = st.slider("Slow SMA", 20, 50, 30)
    else:
        rsi_period = st.slider("RSI Period", 5, 30, 14)
        rsi_low = st.slider("Buy Level", 10, 40, 30)
        rsi_high = st.slider("Sell Level", 60, 90, 70)

# Backtest Execution
if st.button("▶️ Run Test", type="primary"):
    with st.spinner("Analyzing..."):
        data = get_data(pair, year, timeframe)
        if data is None:
            st.stop()
            
        # Validate data length
        if len(data) < max(fast if strategy=="SMA Crossover" else rsi_period, 30):
            st.error(f"⚠️ Need at least {max(fast if strategy=='SMA Crossover' else rsi_period, 30)} data points")
            st.stop()
            
        cerebro = bt.Cerebro()
        cerebro.adddata(data)
        cerebro.broker.setcash(10000)
        cerebro.broker.setcommission(0.0002)
        
        if strategy == "SMA Crossover":
            cerebro.addstrategy(SMACrossover, fast=fast, slow=slow)
        else:
            cerebro.addstrategy(RSIStrategy, period=rsi_period, 
                             rsi_low=rsi_low, rsi_high=rsi_high)
        
        # Lightweight analysis for mobile
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        
        try:
            results = cerebro.run()[0]
            st.success("✅ Backtest Complete")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Final Value", f"${cerebro.broker.getvalue():,.2f}")
                st.metric("Sharpe Ratio", 
                         f"{results.analyzers.sharpe.get_analysis()['sharperatio']:.2f}")
            with col2:
                st.metric("Annual Return", 
                         f"{results.analyzers.returns.get_analysis()['rnorm100']:.1f}%")
                
            # Simple mobile-friendly plot
            st.line_chart(pd.DataFrame({
                'Price': [x.close for x in data]
            }))
            
        except Exception as e:
            st.error(f"Backtest failed: {str(e)}")
