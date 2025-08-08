import pandas as pd
import numpy as np

def calculate_indicators(df):
    # MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Bollinger Bands
    df['20_MA'] = df['Close'].rolling(window=20).mean()
    df['20_STD'] = df['Close'].rolling(window=20).std()
    df['Upper_BB'] = df['20_MA'] + (df['20_STD'] * 2)
    df['Lower_BB'] = df['20_MA'] - (df['20_STD'] * 2)

    return df

def generate_signals(df):
    df = df.copy()

    # Drop rows with NaN in key indicator columns to avoid errors
    df = df.dropna(subset=['MACD', 'Signal_Line', 'RSI', 'Lower_BB', 'Upper_BB'])

    df['Buy'] = (
        (df['MACD'] > df['Signal_Line']) & (df['MACD'].shift(1) <= df['Signal_Line'].shift(1)) &
        (df['RSI'] < 30) &
        (df['Close'] <= df['Lower_BB'])
    ).fillna(False)

    df['Sell'] = (
        (df['MACD'] < df['Signal_Line']) & (df['MACD'].shift(1) >= df['Signal_Line'].shift(1)) &
        (df['RSI'] > 70) &
        (df['Close'] >= df['Upper_BB'])
    ).fillna(False)

    df['Signal'] = 0
    df.loc[df['Buy'], 'Signal'] = 1
    df.loc[df['Sell'], 'Signal'] = -1

    return df

def backtest_signals(df):
    df = df.copy()
    positions = []
    returns = []

    position_open = False
    buy_price = 0

    for idx, row in df.iterrows():
        if row['Signal'] == 1 and not position_open:
            buy_price = row['Close']
            position_open = True
            positions.append(('Buy', idx, buy_price))
        elif row['Signal'] == -1 and position_open:
            sell_price = row['Close']
            ret = (sell_price - buy_price) / buy_price
            returns.append(ret)
            positions.append(('Sell', idx, sell_price))
            position_open = False

    total_return = np.prod([1 + r for r in returns]) - 1 if returns else 0
    win_trades = sum([1 for r in returns if r > 0])
    loss_trades = sum([1 for r in returns if r <= 0])
    total_trades = len(returns)

    return {
        'total_return': total_return,
        'win_rate': win_trades / total_trades if total_trades else 0,
        'total_trades': total_trades,
        'positions': positions,
        'returns': returns
    }
