import backtrader as bt

class SMACrossover(bt.Strategy):
    params = (
        ('fast', 10),
        ('slow', 30),
        ('min_data_points', 50)  # Safety threshold
    )
    
    def __init__(self):
        # Validate data length first
        if len(self.data) < self.p.min_data_points:
            raise ValueError(f"Need {self.p.min_data_points} data points minimum")
            
        self.sma_fast = bt.indicators.SMA(period=self.p.fast)
        self.sma_slow = bt.indicators.SMA(period=self.p.slow)
        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)
        
    def next(self):
        # Skip if not enough data
        if len(self.data) < self.p.slow or len(self.sma_fast) < 1:
            return
            
        if not self.position and self.crossover > 0:
            self.buy()
        elif self.position and self.crossover < 0:
            self.close()

class RSIStrategy(bt.Strategy):
    params = (
        ('period', 14),
        ('rsi_low', 30),
        ('rsi_high', 70),
        ('min_data_points', 30)
    )
    
    def __init__(self):
        if len(self.data) < self.p.min_data_points:
            raise ValueError(f"Need {self.p.min_data_points} data points minimum")
            
        self.rsi = bt.indicators.RSI(
            self.data.close,
            period=self.p.period,
            safediv=True,  # Prevent division errors
            upperband=self.p.rsi_high,
            lowerband=self.p.rsi_low
        )
        
    def next(self):
        if len(self.rsi) < 1:  # Wait for RSI to initialize
            return
            
        if not self.position and self.rsi[0] < self.p.rsi_low:
            self.buy()
        elif self.position and self.rsi[0] > self.p.rsi_high:
            self.close()
