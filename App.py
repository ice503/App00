import streamlit as st
import backtrader as bt
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from strategies import SMACrossover, RSIStrategy

# Configure app for mobile
st.set_page_config(
    layout="wide",
    page_title="📊 Forex Strategy Tester",
    initial_sidebar_state="expanded"
)

@st.cache_data(ttl=3600, show_spinner=True)
def get_data(pair="EURUSD=X", year=2023, timeframe="Daily"):
    """Robust data loader with multiple fallbacks"""
    try:
        # 1. Primary attempt with exact dates
        interval = "1h" if timeframe == "Hourly" else "1d"
        end_date = datetime(year, 12, 31)
        start_date = datetime(year, 1, 1)
        
        df = yf.download(
            pair,
            start=start_date,
            end=end_date + timedelta(days=1),  # Include end date
            interval=interval,
            progress=False,
            repair=True,
            timeout=15
        )
        
        # 2. Fallback to Yahoo's built-in period
        if len(df) == 0:
            df = yf.download(
                pair,
                period="1y",
                interval=interval,
                repair=True
            )
            df = df.loc[str(year)]  # Filter to requested year
            
        # 3. Final fallback to cached data
        if len(df) == 0:
            raise ValueError("No data from Yahoo, using backup")
            
        # Standardize data format
        df = df.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }).dropna()
        
        # Convert to backtrader format
        data = bt.feeds.PandasData(
            dataname=df[['open','high','low','close','volume']],
            datetime=None,  # Use index as datetime
            open=0, high=1, low=2, close=3, volume=4
        )
        return data
        
    except Exception as e:
        st.error(f"""
        🔴 Data Loading Failed
        Error: {str(e)}
        Trying backup data...
        """)
        # Emergency fallback data
        try:
            from backtrader.feeds import YahooFinanceData
            return YahooFinanceData(
                dataname='EURUSD=X',
                fromdate=datetime(2023,1,1),
                todate=datetime(2023,12,31)
            )
        except:
            st.stop()

# UI Controls
with st.sidebar:
    st.header("Parameters")
    pair = st.selectbox("Currency Pair", [
        "EURUSD=X", 
        "GBPUSD=X", 
        "USDJPY=X",
        "AUDUSD=X"
    ], index=0)
    year = st.selectbox("Year", [2023, 2022, 2021], index=0)
    timeframe = st.radio("Timeframe", ["Daily", "Hourly"], index=0)
    
    strategy = st.selectbox("Strategy", [
        "SMA Crossover", 
        "RSI"
    ])
    
    if strategy == "SMA Crossover":
        fast = st.slider("Fast SMA", 5, 20, 10)
        slow = st.slider("Slow SMA", 20, 50, 30)
    else:
        rsi_period = st.slider("RSI Period", 5, 30, 14)
        rsi_low = st.slider("Buy Level", 10, 40, 30)
        rsi_high = st.slider("Sell Level", 60, 90, 70)

# Backtest Execution
if st.button("▶️ Run Analysis", type="primary"):
    with st.spinner("Running backtest..."):
        data = get_data(pair, year, timeframe)
        
        if data is None:
            st.error("Unable to load any market data")
            st.stop()
            
        # Initialize engine
        cerebro = bt.Cerebro()
        cerebro.adddata(data)
        cerebro.broker.setcash(10000)
        cerebro.broker.setcommission(0.0002)
        
        # Add strategy
        if strategy == "SMA Crossover":
            cerebro.addstrategy(SMACrossover, fast=fast, slow=slow)
        else:
            cerebro.addstrategy(RSIStrategy, 
                              period=rsi_period,
                              rsi_low=rsi_low,
                              rsi_high=rsi_high)
        
        # Lightweight analysis for mobile
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        
        try:
            results = cerebro.run()[0]
            
            # Display results
            st.success("✅ Backtest Completed")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Final Value", f"${cerebro.broker.getvalue():,.2f}")
                st.metric("Sharpe Ratio", 
                         f"{results.analyzers.sharpe.get_analysis()['sharperatio']:.2f}")
            with col2:
                st.metric("Annual Return",
                         f"{results.analyzers.returns.get_analysis()['rnorm100']:.1f}%")
                st.metric("Max Drawdown",
                         f"{results.analyzers.drawdown.get_analysis()['max']['drawdown']:.1f}%")
            
            # Simple mobile plot
            st.line_chart(pd.DataFrame({
                'Price': [data.close[i] for i in range(len(data))]
            }))
            
        except Exception as e:
            st.error(f"Backtest failed: {str(e)}")
