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
    df['hl2'] = (df['high'] + df['low']) / 2
    df = atr(df, atr_period)  # Assuming the atr function is defined as before
    df['up'] = df['hl2'] - (atr_multiplier * df['atr'])
    df['dn'] = df['hl2'] + (atr_multiplier * df['atr'])

    # Initialize columns to hold the final 'up' and 'dn' values
    df['final_up'] = 0.0
    df['final_dn'] = 0.0

    # Iteratively update 'final_up' and 'final_dn' based on the previous close
    for i in range(1, len(df)):
        # Update 'final_up'
        if df['close'][i - 1] > df['final_up'][i - 1]:
            df['final_up'][i] = max(df['up'][i], df['final_up'][i - 1])
        else:
            df['final_up'][i] = df['up'][i]

        # Update 'final_dn'
        if df['close'][i - 1] < df['final_dn'][i - 1]:
            df['final_dn'][i] = min(df['dn'][i], df['final_dn'][i - 1])
        else:
            df['final_dn'][i] = df['dn'][i]

    # Determine the trend
    df['trend'] = np.where(df['close'] > df['final_up'], 1, np.where(df['close'] < df['final_dn'], -1, np.NaN))
    df['trend'].fillna(method='ffill', inplace=True)

    return df


def backtest(df_original, atr_period, atr_multiplier, ma_fast_period, ma_slow_period, ma_signal_period):
    df = df_original.copy()

    # ATR Calculation
    df['high_low'] = df['high'] - df['low']
    df['high_close'] = np.abs(df['high'] - df['close'].shift())
    df['low_close'] = np.abs(df['low'] - df['close'].shift())
    df['ranges'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
    df['atr'] = df['ranges'].rolling(window=atr_period).mean()

    # Supertrend Calculation
    df['hl2'] = (df['high'] + df['low']) / 2
    df['up'] = df['hl2'] - (atr_multiplier * df['atr'])
    df['dn'] = df['hl2'] + (atr_multiplier * df['atr'])

    # Iteratively Update 'up' and 'dn' based on the previous close
    for i in range(1, len(df)):
        if df['close'][i - 1] > df['up'][i - 1]:
            df['up'][i] = max(df['up'][i], df['up'][i - 1])
        if df['close'][i - 1] < df['dn'][i - 1]:
            df['dn'][i] = min(df['dn'][i], df['dn'][i - 1])

    df['trend'] = np.where(df['close'] > df['up'], 1, np.where(df['close'] < df['dn'], -1, np.NaN))
    df['trend'].fillna(method='ffill', inplace=True)

    # MACD Calculation
    df['ema_fast'] = df['close'].ewm(span=ma_fast_period).mean()
    df['ema_slow'] = df['close'].ewm(span=ma_slow_period).mean()
    df['macd'] = df['ema_fast'] - df['ema_slow']
    df['macd_signal'] = df['macd'].rolling(window=ma_signal_period).mean()

    # Signal Calculation
    df['signal'] = 0
    for i in range(1, len(df)):
        if (df['trend'][i] == 1 and df['macd'][i] > df['macd_signal'][i] and
            (df['trend'][i - 1] == -1 or df['macd'][i - 1] < df['macd_signal'][i - 1])):
            df['signal'][i] = 1
        elif (df['trend'][i] == -1 and df['macd'][i] < df['macd_signal'][i] and
              (df['trend'][i - 1] == 1 or df['macd'][i - 1] > df['macd_signal'][i - 1])):
            df['signal'][i] = -1

    # PnL and Drawdown Calculation
    df['pnl'] = df['close'].pct_change() * df['signal'].shift(1)
    df['cum_pnl'] = df['pnl'].cumsum()
    df['max_cum_pnl'] = df['cum_pnl'].cummax()
    df['drawdown'] = df['max_cum_pnl'] - df['cum_pnl']

    return df['pnl'].sum(), df['drawdown'].max()

