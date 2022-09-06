import pandas as pd
import numpy as np


pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", 1000)


def backtest(df_original: pd.DataFrame, ma_period: int, std_multiplier: float):
    df = df_original.copy()

    df["ma"] = df["close"].rolling(window=ma_period).mean()
    df["std"] = df["close"].rolling(window=ma_period).std()
    df["upper"] = df["ma"] + df["std"] * std_multiplier
    df["lower"] = df["ma"] - df["std"] * std_multiplier

    df["signal"] = np.where((df["close"] > df["upper"]) & (df["close"].shift(1) < df["upper"].shift(1)), 1,
                            np.where((df["close"] < df["lower"]) & (df["close"].shift(1) > df["lower"].shift(1)), -1, 0))

    df["close_change"] = df["close"].pct_change()
    df["signal_shift"] = df["signal"].shift(1)
    df["pnl"] = df["close"].pct_change() * df["signal"].shift(1)

    df["cum_pnl"] = df["pnl"].cumsum()
    df["max_cum_pnl"] = df["cum_pnl"].cummax()
    df["drawdown"] = df["max_cum_pnl"] - df["cum_pnl"]

    return df["pnl"].sum(), df["drawdown"].max()