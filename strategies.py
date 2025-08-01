import backtrader as bt

class SMACrossover(bt.Strategy):
    params = (('fast',10), ('slow',30))
    
    def __init__(self):
        # Validate data exists
        if len(self.data) < 10:
            raise ValueError("Insufficient data")
            
        self.sma_fast = bt.indicators.SMA(period=self.p.fast)
        self.sma_slow = bt.indicators.SMA(period=self.p.slow)
        
    def next(self):
        if len(self.data) < self.p.slow:
            return
            
        if not self.position:
            if self.sma_fast[0] > self.sma_slow[0]:
                self.buy()
        else:
            if self.sma_fast[0] < self.sma_slow[0]:
                self.close()
