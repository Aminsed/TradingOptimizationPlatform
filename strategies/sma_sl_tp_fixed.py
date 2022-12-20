import pandas as pd
import numpy as np
import typing
import talib


pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", 1000)

def backtest(data1: pd.core.frame.DataFrame, slow_ma_period: int, fast_ma_period: int, atr_period: int, takeprofit: float ,stoploss: float) -> typing.Tuple[float, float]:
    data = data1.copy()
    data['low'] = data['low'].astype('float')
    data = data.dropna()
    data['high'] = data['high'].astype('float')
    data = data.dropna()
    data['close'] = data['close'].astype('float')
    data = data.dropna()
    data['slow_ma'] = data['close'].rolling(window=slow_ma_period).mean()
    data = data.dropna()
    data['fast_ma'] = data['close'].rolling(window=fast_ma_period).mean()
    data = data.dropna()
    data['atr'] = talib.ATR(data['high'], data['low'], data['close'], timeperiod=atr_period)
    data = data.dropna()
    data["signal"] = np.where(data["fast_ma"] > data["slow_ma"], 1, -1)
    data = data.dropna()

    
    
    number_of_trades = 0
    balance = 1000
    #percentage amount of available balance used for each trade
    invest_per_trade_percent = 100
    cost_per_trade_percent = 0
    open_orders = []
    pending_order={}
    trailing_stoploss = []
    balance_hist = []
    
    for i in range(1, len(data)):
        balance_hist.append(balance)
        
        # remove for validation
        temp_max_dd = max(balance_hist)
        if balance < 800 or balance < (temp_max_dd*0.8):
            balance_hist = [0]
            break

        invest_per_trade = balance * invest_per_trade_percent / 100
        if open_orders:
            if open_orders[0]["trade_side"]==1:

                ###check stoploss level for long                           
                if open_orders[0]["stoploss"] > data['low'].iloc[i]:
                    balance += (open_orders[0]["stoploss"] - open_orders[0]["trade_entry_price"])*invest_per_trade
                    balance -= (cost_per_trade_percent/100 * invest_per_trade)
                    open_orders = []
                    number_of_trades += 1

                ###check take profit for long                 
                elif open_orders[0]["takeprofit"] < data['high'].iloc[i]:
                    balance += (open_orders[0]["takeprofit"] - open_orders[0]["trade_entry_price"])*invest_per_trade
                    balance -= (cost_per_trade_percent/100 * invest_per_trade)
                    open_orders = []
                    number_of_trades += 1
                
                ###check if signal is still valid
                elif data['signal'].iloc[i] == -1:
                    balance += (data["close"].iloc[i] - open_orders[0]["trade_entry_price"])*invest_per_trade
                    balance -= (cost_per_trade_percent/100 * invest_per_trade)
                    open_orders = []
                    number_of_trades += 1



            elif open_orders[0]["trade_side"]==-1:

                ###check stoploss for short                      
                if open_orders[0]["stoploss"] > data['low'].iloc[i]:
                    balance += (open_orders[0]["trade_entry_price"] - open_orders[0]["stoploss"])*invest_per_trade
                    balance -= (cost_per_trade_percent/100 * invest_per_trade)
                    open_orders = []
                    number_of_trades += 1


                ###check take profit for short
                elif open_orders[0]["takeprofit"] > data['low'].iloc[i]:
                    balance += (open_orders[0]["trade_entry_price"] - open_orders[0]["takeprofit"])*invest_per_trade
                    balance -= (cost_per_trade_percent/100 * invest_per_trade)
                    open_orders = []
                    number_of_trades += 1
                
                ###check if signal is still valid
                elif data['signal'].iloc[i] == 1:
                    balance += (open_orders[0]["trade_entry_price"] - data["close"].iloc[i])*invest_per_trade
                    balance -= (cost_per_trade_percent/100 * invest_per_trade)
                    open_orders = []
                    number_of_trades += 1
                                
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

            elif data['signal'].iloc[i] == -1:
                trade_entry_price = data['close'].iloc[i]
                sl = data['close'].iloc[i] + ((data['atr'].iloc[i])*stoploss)
                tp = data['close'].iloc[i] - ((data['atr'].iloc[i])*takeprofit)
                pending_order = {"order_id":i, "trade_side":-1, "trade_entry_price":trade_entry_price,
                                "stoploss":sl, "takeprofit":tp}
    # remove in validation
    if number_of_trades < 150:
        return balance * (number_of_trades/150), max(balance_hist) - balance
    else:
        return balance, max(balance_hist) - balance

