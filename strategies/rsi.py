import pandas as pd
import numpy as np


pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", 1000)


def backtest(df_original: pd.DataFrame, rsi_period: int, ma_period:int):
    df = df_original.copy()

    df["change"] = df["close"].diff()
    df["gain"] = np.where(df["change"] > 0, df["change"], 0)
    df["loss"] = np.where(df["change"] < 0, abs(df["change"]), 0)
    df["avg_gain"] = df["gain"].rolling(window=rsi_period).mean()
    df["avg_loss"] = df["loss"].rolling(window=rsi_period).mean()
    df["rs"] = df["avg_gain"] / df["avg_loss"]
    df["rsi"] = 100 - (100 / (1 + df["rs"]))
    df["rsi_ma"] = df["rsi"].rolling(window=ma_period).mean()

    df["signal"] = np.where((df["rsi"] > df["rsi_ma"]) & (df["rsi"].shift(1) < df["rsi_ma"].shift(1)), 1,
                            np.where((df["rsi"] < df["rsi_ma"]) & (df["rsi"].shift(1) > df["rsi_ma"].shift(1)), -1, 0))

    df["close_change"] = df["close"].pct_change()
    df["signal_shift"] = df["signal"].shift(1)
    df["pnl"] = df["close"].pct_change() * df["signal"].shift(1)

    df["cum_pnl"] = df["pnl"].cumsum()
    df["max_cum_pnl"] = df["cum_pnl"].cummax()
    df["drawdown"] = df["max_cum_pnl"] - df["cum_pnl"]

    return df["pnl"].sum(), df["drawdown"].max()