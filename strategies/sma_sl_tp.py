import pandas as pd
import numpy as np


pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", 1000)


def backtest(df: pd.DataFrame, slow_ma_period: int, fast_ma_period, atr_period: int, stoploss_multiplier: float, takeprofit_multiplier: float):

    df["slow_ma"] = round(df["close"].rolling(window=slow_ma_period).mean(), 2)
    df["fast_ma"] = round(df["close"].rolling(window=fast_ma_period).mean(), 2)
    df["atr"] = round(df["high"].rolling(window=atr_period).max() - df["low"].rolling(window=atr_period).min(), 2)

    df["stoploss"] = df["atr"] * stoploss_multiplier
    df["takeprofit"] = df["atr"] * takeprofit_multiplier

    df["long_entry"] = np.logical_and(df["slow_ma"] > df["fast_ma"], df["close"] > df["slow_ma"])
    df["short_entry"] = np.logical_and(df["slow_ma"] < df["fast_ma"], df["close"] < df["slow_ma"])

    df["long_exit"] = np.logical_or(df["close"] < df["slow_ma"] - df["stoploss"], df["close"] > df["slow_ma"] + df["takeprofit"])
    df["short_exit"] = np.logical_or(df["close"] > df["slow_ma"] + df["stoploss"], df["close"] < df["slow_ma"] - df["takeprofit"])

    df["signal"] = np.nan

    df.loc[df["long_entry"], "signal"] = 1
    df.loc[df["short_entry"], "signal"] = -1
    df.loc[df["long_exit"], "signal"] = 0
    df.loc[df["short_exit"], "signal"] = 0

    df["signal"] = df["signal"].fillna(method="ffill")

    df["close_change"] = df["close"].pct_change()
    df["pnl"] = df["close_change"] * df["signal"]
    df["cum_pnl"] = df["pnl"].cumsum()
    df["max_cum_pnl"] = df["cum_pnl"].cummax()
    df["drawdown"] = df["max_cum_pnl"] - df["cum_pnl"]

    return df["pnl"].sum(), df["drawdown"].max()