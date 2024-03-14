import numpy as np
import pandas as pd

def backtest(df: pd.DataFrame, atr_period: int, atr_multiplier: float, change_atr: int, exponential_ma: int):
    change_atr = bool(change_atr)
    exponential_ma = bool(exponential_ma)
    
    df["ma05"] = df["close"].ewm(span=5).mean() if exponential_ma else df["close"].rolling(window=5).mean()
    df["ma10"] = df["close"].ewm(span=10).mean() if exponential_ma else df["close"].rolling(window=10).mean()
    df["ma15"] = df["close"].ewm(span=15).mean() if exponential_ma else df["close"].rolling(window=15).mean()
    df["ma20"] = df["close"].ewm(span=20).mean() if exponential_ma else df["close"].rolling(window=20).mean()
    df["ma25"] = df["close"].ewm(span=25).mean() if exponential_ma else df["close"].rolling(window=25).mean()
    df["ma30"] = df["close"].ewm(span=30).mean() if exponential_ma else df["close"].rolling(window=30).mean()
    df["ma35"] = df["close"].ewm(span=35).mean() if exponential_ma else df["close"].rolling(window=35).mean()
    df["ma40"] = df["close"].ewm(span=40).mean() if exponential_ma else df["close"].rolling(window=40).mean()
    df["ma45"] = df["close"].ewm(span=45).mean() if exponential_ma else df["close"].rolling(window=45).mean()
    df["ma50"] = df["close"].ewm(span=50).mean() if exponential_ma else df["close"].rolling(window=50).mean()
    df["ma55"] = df["close"].ewm(span=55).mean() if exponential_ma else df["close"].rolling(window=55).mean()
    df["ma60"] = df["close"].ewm(span=60).mean() if exponential_ma else df["close"].rolling(window=60).mean()
    df["ma65"] = df["close"].ewm(span=65).mean() if exponential_ma else df["close"].rolling(window=65).mean()
    df["ma70"] = df["close"].ewm(span=70).mean() if exponential_ma else df["close"].rolling(window=70).mean()
    df["ma75"] = df["close"].ewm(span=75).mean() if exponential_ma else df["close"].rolling(window=75).mean()
    df["ma80"] = df["close"].ewm(span=80).mean() if exponential_ma else df["close"].rolling(window=80).mean()
    df["ma85"] = df["close"].ewm(span=85).mean() if exponential_ma else df["close"].rolling(window=85).mean()
    df["ma90"] = df["close"].ewm(span=90).mean() if exponential_ma else df["close"].rolling(window=90).mean()
    df["ma100"] = df["close"].ewm(span=100).mean() if exponential_ma else df["close"].rolling(window=100).mean()

    df["src"] = df["ma05"]

    df["high_low"] = df["high"] - df["low"]
    df["high_close"] = abs(df["high"] - df["close"].shift(1))
    df["low_close"] = abs(df["low"] - df["close"].shift(1))
    df["tr"] = df[["high_low", "high_close", "low_close"]].max(axis=1)

    df["atr2"] = df["tr"].rolling(window=atr_period).mean()
    df["atr"] = df["tr"].rolling(window=atr_period).mean() if change_atr else df["atr2"]

    df["up"] = df["src"] - (atr_multiplier * df["atr"])
    df["up1"] = df["up"].shift(1).fillna(df["up"])
    df["up"] = np.where(df["close"].shift(1) > df["up1"], df[["up", "up1"]].max(axis=1), df["up"])

    df["dn"] = df["src"] + (atr_multiplier * df["atr"])
    df["dn1"] = df["dn"].shift(1).fillna(df["dn"])
    df["dn"] = np.where(df["close"].shift(1) < df["dn1"], df[["dn", "dn1"]].min(axis=1), df["dn"])

    df["trend"] = 1
    df["trend"] = df["trend"].shift(1).fillna(1)
    df["trend"] = np.where((df["trend"].shift(1) == -1) & (df["close"] > df["dn1"]), 1,
                           np.where((df["trend"].shift(1) == 1) & (df["close"] < df["up1"]), -1, df["trend"]))

    df["signal"] = df["trend"]
    df["close_change"] = df["close"].pct_change()
    df["signal_shift"] = df["signal"].shift(1)
    df["pnl"] = df["close"].pct_change() * df["signal"].shift(1)

    df["cum_pnl"] = df["pnl"].cumsum()
    df["max_cum_pnl"] = df["cum_pnl"].cummax()
    df["drawdown"] = df["max_cum_pnl"] - df["cum_pnl"]

    return df["pnl"].sum(), df["drawdown"].max()