
import datetime
import pandas as pd


from utils import TF_EQUIV
from data_collector import collect_all
from exchanges.binance import BinanceClient
from exchanges.ftx import FtxClient
from exchanges.dukascopy import DukascopyClient

from ctypes import *

from database import Hdf5Client

from utils import get_library, resample_timeframe, STRAT_PARAMS

import strategies.sma_sl_tp

from_time = "2022-01-01"
from_time = int(datetime.datetime.strptime(from_time, "%Y-%m-%d").timestamp() * 1000)
to_time = int(datetime.datetime.now().timestamp() * 1000)
exchange = "Dukascopy"
symbol = "2032"
strategy = "sma_sl_tp"
tf = "1h"

h5_db = Hdf5Client(exchange)
data = h5_db.get_data(symbol, from_time, to_time)
data = resample_timeframe(data, tf)
print(data.head())
df = pd.read_csv("result.csv")


df["bt_pnl"] = df["PNL"]
df["bt_dd"] = df["Max_Drawdown"]


for i in range(len(df)):

    slow_ma_period = df["slow_ma_period"].iloc[i]
    fast_ma_period = df["fast_ma_period"].iloc[i]
    takeprofit = df["takeprofit"].iloc[i]
    stoploss = df["stoploss"].iloc[i]

    df["bt_pnl"].iloc[i], df["bt_dd"].iloc[i] = strategies.sma_sl_tp.backtest(data, slow_ma_period, 
    fast_ma_period, takeprofit, stoploss)



df = df.sort_values(by=['bt_pnl'], ascending=False)


df.to_csv(symbol+'_final'+'.csv')
