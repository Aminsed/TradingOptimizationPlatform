import logging
import datetime

import backtester
import optimizer
from utils import TF_EQUIV
from data_collector import collect_all
from exchanges.binance import BinanceClient
from exchanges.gaincapital import GCapiClient
from exchanges.dukascopy import DukascopyClient
from tqdm import tqdm
import matplotlib.pyplot as plt



logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s %(levelname)s :: %(message)s")

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler("info.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)


if __name__ == "__main__":

    mode = input("Choose the program mode (data / backtest / optimize): ").lower()

    while True:
        exchange = input("Choose an exchange: ").lower()
        if exchange in ["gaincapital", "binance", "dukascopy"]:
            break
        else:
            print(exchange + " is not a valid exchange.")
            print("Please select from: gaincapital, binance, dukascopy")

    if exchange == "binance":
        client = BinanceClient(True)
    elif exchange == "gaincapital":
        client = GCapiClient()
    elif exchange == "dukascopy":
        client = DukascopyClient()

    #modify get symbol to read from csv and txt files instead
    # while True:
    symbol = input("Choose a symbol: ").upper()
        # if symbol in client.symbols:
        #     break
        # else:
        #     print("Symbol not found.")

    if mode == "data":
        collect_all(client, exchange, symbol)

    elif mode in ["backtest", "optimize"]:


        available_strategies = ["bb", "ichimoku", "macd", "obv", "psar", 
                                "rsi", "sma", "sma_sl_tp", "sma_sl_tp_fixed",
                                 "sup_res", "super_macd", "madrid_trend"]

        while True:
            strategy = input(f"Choose a strategy ({', '.join(available_strategies)}): ").lower()
            if strategy in available_strategies:
                break

        # Timeframe

        while True:
            tf = input(f"Choose a timeframe ({', '.join(TF_EQUIV.keys())}): ").lower()
            if tf in TF_EQUIV.keys():
                break

        # From

        while True:
            from_time = input("Backtest from (yyyy-mm-dd or Press Enter): ")
            if from_time == "":
                from_time = 0
                break

            try:
                from_time = int(datetime.datetime.strptime(from_time, "%Y-%m-%d").timestamp() * 1000)
                break
            except ValueError:
                continue

        while True:
            to_time = input("Backtest to (yyyy-mm-dd or Press Enter): ")
            if to_time == "":
                to_time = int(datetime.datetime.now().timestamp() * 1000)
                break

            try:
                to_time = int(datetime.datetime.strptime(to_time, "%Y-%m-%d").timestamp() * 1000)
                break
            except ValueError:
                continue

    if mode == "backtest":
        print(backtester.run(exchange, symbol, strategy, tf, from_time, to_time))
    elif mode == "optimize":

        # Population size

        while True:
            try:
                pop_size = int(input(f"Choose a population size: "))
                break
            except ValueError:
                continue

        # Generations
        while True:
            try:
                generations = int(input(f"Choose a number of generations: "))
                break
            except ValueError:
                continue
        
        NSGA3 = optimizer.NSGA3(exchange, symbol, strategy, tf, from_time, to_time, pop_size)


        p_population = NSGA3.create_initial_population()
        p_population = NSGA3.evaluate_population(p_population)
        p_population = NSGA3.crowding_distance(p_population)

        g = 0

        pbar = tqdm(total=generations)
        while g < generations:

            q_population = NSGA3.create_offspring_population(p_population)
            q_population = NSGA3.evaluate_population(q_population)
            #
            pnl_values = [backtest.pnl for backtest in p_population]
            max_dd_values = [backtest.max_dd for backtest in p_population]
            plt.scatter(max_dd_values, pnl_values)
            plt.ylabel("PNL")
            plt.xlabel("Max. Drawdown")
            plt.title(f"Population over {g} Generations")
            plt.show(block=False)
            plt.pause(0.5)
            plt.clf()
            #
            r_population = p_population + q_population

            NSGA3.population_params.clear()

            i = 0
            population = dict()
            for bt in r_population:
                bt.reset_results()
                NSGA3.population_params.append(bt.parameters)
                population[i] = bt
                i += 1


            fronts = NSGA3.non_dominated_sortings(population)
            for j in range(len(fronts)):
                fronts[j] = NSGA3.crowding_distance(fronts[j])

            p_population = NSGA3.create_new_population(fronts)

            pbar.update(1)
            g +=1
        pbar.close()
        plt.show()

        print("\n")
        
        with open('result.txt', 'w') as f:
            for individual in p_population:
                f.write(str(individual) + '\n')
