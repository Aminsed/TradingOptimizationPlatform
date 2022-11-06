def backtest(df: pd.DataFrame, slow_ma: int, fast_ma: int):

    df["slow_ma"] = round(df["close"].rolling(window=slow_ma).mean(), 2)
    df["fast_ma"] = round(df["close"].rolling(window=fast_ma).mean(), 2)

    df["signal"] = np.where(df["fast_ma"] < df["slow_ma"], 1, -1)
    df["close_change"] = df["close"].pct_change()
    df["signal_shift"] = df["signal"].shift(1)
    df["pnl"] = df["close"].pct_change() * df["signal"].shift(1)

    df["cum_pnl"] = df["pnl"].cumsum()
    df["max_cum_pnl"] = df["cum_pnl"].cummax()
    df["drawdown"] = df["max_cum_pnl"] - df["cum_pnl"]

    return df["pnl"].sum(), df["drawdown"].max()
