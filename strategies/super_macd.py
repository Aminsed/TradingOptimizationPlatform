import pandas as pd
import numpy as np

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", 1000)

def atr(df, period):
    """Calculate True Range and Average True Range"""
    df['high_low'] = df['high'] - df['low']
    df['high_close'] = np.abs(df['high'] - df['close'].shift())
    df['low_close'] = np.abs(df['low'] - df['close'].shift())
    df['ranges'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
    df['atr'] = df['ranges'].rolling(window=period).mean()
    return df

def supertrend(df, atr_period, atr_multiplier):
    """Calculate Supertrend"""
    df['hl2'] = (df['high'] + df['low']) / 2
    df = atr(df, atr_period)
    df['up'] = df['hl2'] - (atr_multiplier * df['atr'])
    df['dn'] = df['hl2'] + (atr_multiplier * df['atr'])
    df['up1'] = df['up'].shift().where(df['close'].shift() > df['up'].shift(), df['up'])
    df['dn1'] = df['dn'].shift().where(df['close'].shift() < df['dn'].shift(), df['dn'])
    df['trend'] = np.where(df['close'] > df['up1'], 1, np.where(df['close'] < df['dn1'], -1, np.NaN))
    df['trend'].fillna(method='ffill', inplace=True)
    return df

def backtest(df_original, atr_period, atr_multiplier, ma_fast_period, ma_slow_period, ma_signal_period):
    df = df_original.copy()
    
    # Supertrend Calculation
    df = supertrend(df, atr_period, atr_multiplier)
    
    # MACD Calculation
    df['ema_fast'] = df['close'].ewm(span=ma_fast_period).mean()
    df['ema_slow'] = df['close'].ewm(span=ma_slow_period).mean()
    df['macd'] = df['ema_fast'] - df['ema_slow']
    df['macd_signal'] = df['macd'].ewm(span=ma_signal_period).mean()
    
    # Signals
    df['buy_signal'] = (df['trend'] == 1) & (df['macd'] > df['macd_signal']) & ((df['trend'].shift() == -1) | (df['macd'].shift() < df['macd_signal'].shift()))
    df['sell_signal'] = (df['trend'] == -1) & (df['macd'] < df['macd_signal']) & ((df['trend'].shift() == 1) | (df['macd'].shift() > df['macd_signal'].shift()))
    
    # PnL Calculation
    df['signal'] = np.where(df['buy_signal'], 1, np.where(df['sell_signal'], -1, 0))
    df['pnl'] = df['close'].pct_change() * df['signal'].shift(1)
    
    # Drawdown Calculation
    df['cum_pnl'] = df['pnl'].cumsum()
    df['max_cum_pnl'] = df['cum_pnl'].cummax()
    df['drawdown'] = df['max_cum_pnl'] - df['cum_pnl']
    
    return df['pnl'].sum(), df['drawdown'].max()
