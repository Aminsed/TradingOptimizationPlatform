import datetime
from ctypes import *

import pandas as pd


TF_EQUIV = {"1m": "1Min", "5m": "5Min", "15m": "15Min", "30m": "30Min", "1h": "1H", "4h": "4H", "12h": "12H", "1d": "D"}

STRAT_PARAMS = {
    "obv": {
        "ma_period": {"name": "MA Period", "type": int, "min": 2, "max": 500},
    },
    "ichimoku": {
        "kijun": {"name": "Kijun Period", "type": int, "min": 2, "max": 500},
        "tenkan": {"name": "Tenkan Period", "type": int, "min": 2, "max": 500},
    },
    "sup_res": {
        "min_points": {"name": "Min. Points", "type": int, "min": 2, "max": 20},
        "min_diff_points": {"name": "Min. Difference between Points", "type": int, "min": 2, "max": 100},
        "rounding_nb": {"name": "Rounding Number", "type": float, "min": 10, "max": 500, "decimals": 2},
        "take_profit": {"name": "Take Profit %", "type": float, "min": 1, "max": 40, "decimals": 2},
        "stop_loss": {"name": "Stop Loss %", "type": float, "min": 2, "max": 40, "decimals": 2},
    },
    "sma": {
        "slow_ma": {"name": "Slow MA Period", "type": int, "min": 1, "max": 2000},
        "fast_ma": {"name": "Fast MA Period", "type": int, "min": 1, "max": 2000},
        },
    "psar": {
        "initial_acc": {"name": "Initial Acceleration", "type": float, "min": 0.01, "max": 1.0, "decimals": 2},
        "acc_increment": {"name": "Acceleration Increment", "type": float, "min": 0.01, "max": 1.0, "decimals": 2},
        "max_acc": {"name": "Max Acceleration", "type": float, "min": 0.01, "max": 1, "decimals": 2},
        },
    "macd": {
        "ma_slow_period": {"name": "Slow MA Period", "type": int, "min": 2, "max": 500},
        "ma_fast_period": {"name": "Fast MA Period", "type": int, "min": 2, "max": 500},
        "ma_signal_period": {"name": "Signal MA Period", "type": int, "min": 2, "max": 500},
        },
    "rsi": {
        "rsi_period": {"name": "RSI Period", "type": int, "min": 2, "max": 500},
        "ma_period": {"name": "MA Period", "type": int, "min": 2, "max": 500},
        },
    "bb": {
        "ma_period": {"name": "MA Period", "type": int, "min": 2, "max": 500},
        "std_multiplier": {"name": "Std. Multiplier", "type": float, "min": 0.01, "max": 5.0, "decimals": 2},
    },
    "sma_sl_tp": {
        "slow_ma_period": {"name": "Slow MA Period", "type": int, "min": 1, "max": 1000},
        "fast_ma_period": {"name": "Fast MA Period", "type": int, "min": 1, "max": 1000},
        "atr_period": {"name": "ATR Period", "type": int, "min": 100, "max": 1000},
        "takeprofit": {"name": "Take Profit", "type": float, "min": 2.00, "max": 20, "decimals": 2},
        "stoploss": {"name": "Stop Loss", "type": float, "min": 2.00, "max": 20, "decimals": 2},
    },
    "sma_sl_tp_fixed": {
        "slow_ma_period": {"name": "Slow MA Period", "type": int, "min": 1, "max": 2000},
        "fast_ma_period": {"name": "Fast MA Period", "type": int, "min": 1, "max": 1000},
        "atr_period": {"name": "ATR Period", "type": int, "min": 100, "max": 2000},
        "takeprofit": {"name": "Take Profit", "type": float, "min": 2.00, "max": 20.00, "decimals": 2},
        "stoploss": {"name": "Stop Loss", "type": float, "min": 2.00, "max": 20.00, "decimals": 2},
    },

}


def ms_to_dt(ms: int) -> datetime.datetime:
    return datetime.datetime.utcfromtimestamp(ms / 1000)


def resample_timeframe(data: pd.DataFrame, tf: str) -> pd.DataFrame:
    return data.resample(TF_EQUIV[tf]).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    )

def get_library():
    lib = CDLL("backtestingCpp/build/libbacktestingCpp.dylib")

    #SMA
    lib.Sma_new.restype = c_void_p
    lib.Sma_new.argtypes = [c_char_p, c_char_p, c_char_p, c_longlong, c_longlong]
    lib.Sma_execute_backtest.restype = c_void_p
    lib.Sma_execute_backtest.argtypes = [c_void_p, c_int, c_int] #ptr to class, slow_ma, fast_ma

    lib.Sma_get_pnl.restype = c_double
    lib.Sma_get_pnl.argtypes = [c_void_p]
    lib.Sma_get_max_dd.restype = c_double
    lib.Sma_get_max_dd.argtypes = [c_void_p]

    #PSAR
    lib.Psar_new.restype = c_void_p
    lib.Psar_new.argtypes = [c_char_p, c_char_p, c_char_p, c_longlong, c_longlong]
    lib.Psar_execute_backtest.restype = c_void_p
    lib.Psar_execute_backtest.argtypes = [c_void_p, c_double, c_double, c_double]

    lib.Psar_get_pnl.restype = c_double
    lib.Psar_get_pnl.argtypes = [c_void_p]
    lib.Psar_get_max_dd.restype = c_double
    lib.Psar_get_max_dd.argtypes = [c_void_p]

    return lib
