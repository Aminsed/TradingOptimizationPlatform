import pandas as pd
import numpy as np
import typing
import talib


pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", 1000)

def backtest(data1: pd.core.frame.DataFrame, slow_ma_period: int, fast_ma_period: int,takeprofit: float ,stoploss: float) -> typing.Tuple[float, float]:
    data = data1.copy()
    data['low'] = data['low'].astype('float')
    data['high'] = data['high'].astype('float')
    data['close'] = data['close'].astype('float')
    data['slow_ma'] = data['close'].rolling(window=slow_ma_period).mean()
    data['fast_ma'] = data['close'].rolling(window=fast_ma_period).mean()
    data['atr'] = talib.ATR(data['high'], data['low'], data['close'], timeperiod=fast_ma_period)
    data = data.dropna()
    data["signal"] = np.where(data["fast_ma"] > data["slow_ma"], 1, -1)


    
    
    number_of_trades = 0
    balance = 100
    #percentage amount of available balance used for each trade
    invest_per_trade_percent = 100
    cost_per_trade_percent = 2
    open_orders = []
    pending_order={}
    trailing_stoploss = []
    balance_hist = []
    
    for i in range(1, len(data)):
        balance_hist.append(balance)

        invest_per_trade = balance * invest_per_trade_percent / 100
        if open_orders:
            if open_orders[0]["trade_side"]==1:

                ###check stoploss level for long                           
                if open_orders[0]["stoploss"] > data['low'].iloc[i]:
                    balance += (open_orders[0]["stoploss"] - open_orders[0]["trade_entry_price"])*invest_per_trade
                    balance -= (cost_per_trade_percent/100 * invest_per_trade)
                    open_orders = []
                    trailing_stoploss = []
                    number_of_trades += 1

                ###check take profit for long                 
                elif open_orders[0]["takeprofit"] < data['high'].iloc[i]:
                    balance += (open_orders[0]["takeprofit"] - open_orders[0]["trade_entry_price"])*invest_per_trade
                    balance -= (cost_per_trade_percent/100 * invest_per_trade)
                    open_orders = []
                    trailing_stoploss = []
                    number_of_trades += 1
                
                ###check if signal is still valid
                elif data['signal'].iloc[i] == -1:
                    balance += (data["close"].iloc[i] - open_orders[0]["trade_entry_price"])*invest_per_trade
                    balance -= (cost_per_trade_percent/100 * invest_per_trade)
                    open_orders = []
                    trailing_stoploss = []
                    number_of_trades += 1

                ### update trailing stoploss for long                        
                elif data['high'].iloc[i] > data['high'].iloc[i-1]:
                        if len(trailing_stoploss) == 0:
                            trailing_stoploss.append(data['high'].iloc[i])
                            dist = data['high'].iloc[i] - data['high'].iloc[i-1]
                            open_orders[0]["stoploss"] += abs(dist)

                        elif data['high'].iloc[i] > max(trailing_stoploss):
                            dist = data['high'].iloc[i] - max(trailing_stoploss) 
                            trailing_stoploss.append(data['high'].iloc[i])
                            open_orders[0]["stoploss"] += abs(dist)


            elif open_orders[0]["trade_side"]==-1:

                ###check stoploss for short                      
                if open_orders[0]["stoploss"] > data['low'].iloc[i]:
                    balance += (open_orders[0]["trade_entry_price"] - open_orders[0]["stoploss"])*invest_per_trade
                    balance -= (cost_per_trade_percent/100 * invest_per_trade)
                    open_orders = []
                    trailing_stoploss = []
                    number_of_trades += 1


                ###check take profit for short
                elif open_orders[0]["takeprofit"] > data['low'].iloc[i]:
                    balance += (open_orders[0]["trade_entry_price"] - open_orders[0]["takeprofit"])*invest_per_trade
                    balance -= (cost_per_trade_percent/100 * invest_per_trade)
                    open_orders = []
                    trailing_stoploss = []
                    number_of_trades += 1
                
                ###check if signal is still valid
                elif data['signal'].iloc[i] == 1:
                    balance += (open_orders[0]["trade_entry_price"] - data["close"].iloc[i])*invest_per_trade
                    balance -= (cost_per_trade_percent/100 * invest_per_trade)
                    open_orders = []
                    trailing_stoploss = []
                    number_of_trades += 1


                ###update stoploss for short
                elif i and open_orders:    
                    if data['low'].iloc[i] < data['low'].iloc[i-1]:
                        if len(trailing_stoploss) == 0:
                            trailing_stoploss.append(data['low'].iloc[i])
                            dist = data['low'].iloc[i] - data['low'].iloc[i-i]
                            open_orders[0]["stoploss"] -= abs(dist)
                        
                        elif data['low'].iloc[i] < min(trailing_stoploss):
                            dist = min(trailing_stoploss) - data['low'].iloc[i] 
                            trailing_stoploss.append(data['low'].iloc[i])
                            open_orders[0]["stoploss"] -= abs(dist)
                                
        #create an active (open) order
        if pending_order and len(open_orders)== 0:
            if pending_order["trade_side"]==1:
                if pending_order["trade_entry_price"] < data['high'].iloc[i]:
                    open_orders.append(pending_order)
                    pending_order = {}

            elif pending_order["trade_side"]==-1:
                if pending_order["trade_entry_price"] > data['low'].iloc[i]:
                    open_orders.append(pending_order)
                    pending_order = {}
            else:
                pending_order = {}


        if not pending_order:
            if data['signal'].iloc[i] == 1:
                trade_entry_price = data['close'].iloc[i]
                sl = data['close'].iloc[i] - ((data['atr'].iloc[i])*stoploss)
                tp = data['close'].iloc[i] + ((data['atr'].iloc[i])*takeprofit)
                pending_order = {"order_id":i,"trade_side":1, "trade_entry_price":trade_entry_price,
                                "stoploss":sl, "takeprofit":tp}

            if data['signal'].iloc[i] == -1:
                trade_entry_price = data['close'].iloc[i]
                sl = data['close'].iloc[i] + ((data['atr'].iloc[i])*stoploss)
                tp = data['close'].iloc[i] - ((data['atr'].iloc[i])*takeprofit)
                pending_order = {"order_id":i, "trade_side":-1, "trade_entry_price":trade_entry_price,
                                "stoploss":sl, "takeprofit":tp}
    #change to 0 in final backtest
    if number_of_trades <= 1:
        return 0, 0
    else:
        max_dd = max(balance_hist) - balance
        return balance, max_dd#(number_of_trades * max_dd) - (balance)
