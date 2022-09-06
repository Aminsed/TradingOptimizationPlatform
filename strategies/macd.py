import pandas as pd
import numpy as np


pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", 1000)


def backtest(df_original: pd.DataFrame, ma_fast_period: int, ma_slow_period: int, ma_signal_period: int):

    df = df_original.copy()

    df["macd"] = df["close"].ewm(span=ma_fast_period).mean() - df["close"].ewm(span=ma_slow_period).mean()
    df["macd_signal"] = df["macd"].ewm(span=ma_signal_period).mean()
    df["macd_diff"] = df["macd"] - df["macd_signal"]

    df["signal"] = np.where(df["macd_diff"] > 0, 1, 0)
    df["close_change"] = df["close"].pct_change()
    df["signal_shift"] = df["signal"].shift(1)
    df["pnl"] = df["close"].pct_change() * df["signal"].shift(1)

    df["cum_pnl"] = df["pnl"].cumsum()
    df["max_cum_pnl"] = df["cum_pnl"].cummax()
    df["drawdown"] = df["max_cum_pnl"] - df["cum_pnl"]

    return df["pnl"].sum(), df["drawdown"].max()