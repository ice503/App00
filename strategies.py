import backtrader as bt

class SMACrossover(bt.Strategy):
    params = (
        ('fast', 10),
        ('slow', 30),
        ('safe_mode', True)  # New safety flag
    )
    
    def __init__(self):
        self.sma_fast = bt.indicators.SMA(period=self.p.fast)
        self.sma_slow = bt.indicators.SMA(period=self.p.slow)
        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)
        
    def next(self):
        # Array bounds protection
        if self.p.safe_mode and (len(self.data) < self.p.slow or len(self.sma_fast) < 1):
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
        ('safe_mode', True)
    )
    
    def __init__(self):
        self.rsi = bt.indicators.RSI(
            self.data.close, 
            period=self.p.period,
            safediv=True  # Prevent division errors
        )
        
    def next(self):
        # Array bounds protection
        if self.p.safe_mode and len(self.rsi) < 1:
            return
            
        if not self.position and self.rsi < self.p.rsi_low:
            self.buy()
        elif self.position and self.rsi > self.p.rsi_high:
            self.close()
