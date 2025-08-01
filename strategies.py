import backtrader as bt

class SMACrossover(bt.Strategy):
    params = (
        ('fast', 10),
        ('slow', 30),
        ('printlog', False)
    )
    
    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()}, {txt}')
    
    def __init__(self):
        self.fast_sma = bt.indicators.SMA(period=self.p.fast)
        self.slow_sma = bt.indicators.SMA(period=self.p.slow)
        self.crossover = bt.indicators.CrossOver(self.fast_sma, self.slow_sma)
        self.order = None
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
            
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.5f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.5f}')
        
        self.order = None
    
    def next(self):
        if self.order:
            return
            
        if not self.position:
            if self.crossover > 0:
                self.log(f'BUY CREATE, {self.datas[0].close[0]:.5f}')
                self.order = self.buy()
        else:
            if self.crossover < 0:
                self.log(f'SELL CREATE, {self.datas[0].close[0]:.5f}')
                self.order = self.sell()

class RSIStrategy(bt.Strategy):
    params = (
        ('period', 14),
        ('rsi_low', 30),
        ('rsi_high', 70),
        ('printlog', False)
    )
    
    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, 
                                    period=self.p.period)
        self.order = None
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
            
        if order.status in [order.Completed]:
            if order.isbuy():
                print(f'BUY EXECUTED at {order.executed.price:.5f}')
            elif order.issell():
                print(f'SELL EXECUTED at {order.executed.price:.5f}')
        
        self.order = None
    
    def next(self):
        if self.order:
            return
            
        if not self.position:
            if self.rsi < self.p.rsi_low:
                self.order = self.buy()
        elif self.rsi > self.p.rsi_high:
            self.order = self.close()
