import backtrader as bt

class SMACrossover(bt.Strategy):
    params = (('fast', 10), ('slow', 30))
    
    def __init__(self):
        self.fast_sma = bt.indicators.SMA(period=self.p.fast)
        self.slow_sma = bt.indicators.SMA(period=self.p.slow)
        self.crossover = bt.indicators.CrossOver(self.fast_sma, self.slow_sma)
    
    def next(self):
        if not self.position and self.crossover > 0:
            self.buy()
        elif self.position and self.crossover < 0:
            self.close()

class RSIStrategy(bt.Strategy):
    params = (('period', 14), ('rsi_low', 30), ('rsi_high', 70))
    
    def __init__(self):
        self.rsi = bt.indicators.RSI(period=self.p.period)
    
    def next(self):
        if not self.position and self.rsi < self.p.rsi_low:
            self.buy()
        elif self.position and self.rsi > self.p.rsi_high:
            self.close()
