import random
import typing
import copy


from regex import B

from utils import STRAT_PARAMS, resample_timeframe, get_library

from database import Hdf5Client
from models import BacktestResult

import multiprocessing as mp

import strategies.obv
import strategies.ichimoku
import strategies.support_resistance
import strategies.macd
import strategies.rsi
import strategies.bb
import strategies.sma_sl_tp
import strategies.sma_sl_tp_fixed



class Nsga2:
    def __init__(self,exchange: str, symbol: str, strategy: str, 
                tf: str, from_time: int, to_time: int, population_size: int):
        self.exchange = exchange
        self.symbol = symbol
        self.strategy = strategy
        self.tf = tf
        self.from_time = from_time
        self.to_time = to_time
        self.population_size = population_size
        
        self.params_data = STRAT_PARAMS[strategy]

        self.population_params = []

        if self.strategy in ["obv", "ichimoku", "sup_res", "macd", "rsi", "bb", "sma_sl_tp", "sma_sl_tp_fixed"]:
            h5_db = Hdf5Client(exchange)
            self.data = h5_db.get_data(symbol, from_time, to_time)
            self.data = resample_timeframe(self.data, tf)

        elif self.strategy in ["sma", "psar"]:
            
            self.lib = get_library()

            if self.strategy == "sma":
                self.obj = self.lib.Sma_new(exchange.encode(), symbol.encode(), tf.encode(), from_time, to_time)
            
            elif self.strategy == "psar":
                self.obj = self.lib.Psar_new(exchange.encode(), symbol.encode(), tf.encode(), from_time, to_time)



    def create_initial_population(self) -> typing.List[BacktestResult]:

        population = []

        while len(population) < self.population_size:
            backtest = BacktestResult()
            for p_code, p in self.params_data.items():
                if p["type"] == int:
                    backtest.parameters[p_code] = random.randint(p["min"], p["max"])
                elif p["type"] == float:
                    backtest.parameters[p_code] = round(random.uniform(p["min"], p["max"]), p["decimals"])

            if backtest not in population:
                population.append(backtest)
                self.population_params.append(backtest.parameters)
        
        return population


    def crowding_distance(self, population: typing.List[BacktestResult]) -> typing.List[BacktestResult]:

        for objective in ["pnl", "max_dd"]:

            population = sorted(population, key=lambda x: getattr(x, objective))
            min_value = getattr(min(population, key=lambda x: getattr(x, objective)), objective)
            max_value = getattr(max(population, key=lambda x: getattr(x, objective)), objective)

            population[0].crowding_distance = float("inf")
            population[-1].crowding_distance = float("inf")


            for i in range(1, len(population) - 1):
                distance = getattr(population[i + 1], objective) - getattr(population[i - 1], objective)
                distance = distance / (max_value - min_value)
                population[i].crowding_distance += distance
        
        return population


    def create_new_population(self, fronts: typing.List[BacktestResult]) -> typing.List[BacktestResult]:
        new_pop = []

        # Calculate crowding distance for each solution in each front
        for front in fronts:
            front = self.crowding_distance(front)

        # Select solutions based on continuous crowded comparison operator
        while len(new_pop) < self.population_size:
            selected_front = None
            selected_solution = None
            min_distance = float("inf")

            # Select front with minimum crowding distance
            for front in fronts:
                if len(front) == 0:
                    continue
                front_min_distance = min([s.crowding_distance for s in front])
                if front_min_distance < min_distance:
                    selected_front = front
                    selected_solution = front[0]
                    min_distance = front_min_distance

            # Add selected solution to new population
            new_pop.append(selected_solution)
            selected_front.remove(selected_solution)

        return new_pop



    def create_offspring_population(self, population: typing.List[BacktestResult]) -> typing.List[BacktestResult]:
        offspring_pop = []
        
        while len(offspring_pop) != self.population_size:

            parents: typing.List[BacktestResult] = []

            for i in range(2):
                random_parents = random.sample(population, k=2)
                if random_parents[0].rank != random_parents[1].rank:
                    best_parent = min(random_parents, key=lambda x: getattr(x, "rank"))
                # If individuals are equal we use crowding distance
                else:
                    best_parent = max(random_parents, key=lambda x: getattr(x, "crowding_distance"))
                
                parents.append(best_parent)

            new_child = BacktestResult()
            # Using copy constructor to make sure child modifications won't change the parents
            new_child.parameters = copy.copy(parents[0].parameters)

            # Crossover

            number_of_crossovers = random.randint(0, len(self.params_data))
            params_to_cross = random.sample(list(self.params_data.keys()), k = number_of_crossovers)

            for p in params_to_cross:
                new_child.parameters[p] = copy.copy(parents[1].parameters[p])

            # Mutation

            number_of_mutations = random.randint(0, len(self.params_data))
            params_to_change = random.sample(list(self.params_data.keys()), k= number_of_mutations)

            for p in params_to_change:
                mutations_strength = random.uniform(-2, 2) # mutation posibilibty of range +-%200
                # Accounting for data type int/float
                new_child.parameters[p] = self.params_data[p]["type"](new_child.parameters[p] * (1 + mutations_strength))
                # Making sure mutation is within expected range of minimum and maximum
                new_child.parameters[p] = max(new_child.parameters[p], self.params_data[p]["min"])
                new_child.parameters[p] = min(new_child.parameters[p], self.params_data[p]["max"])


                if self.params_data[p]["type"] == float:
                    new_child.parameters[p] = round(new_child.parameters[p], self.params_data[p]["decimals"])

            new_child.parameters = self._params_constraints(new_child.parameters)

            # Avoding duplicates
            if new_child.parameters not in self.population_params:
                offspring_pop.append(new_child)
                self.population_params.append(new_child.parameters)

        return offspring_pop






    # Enforcing logical constraints. 
    # For example the slow MA value should always be higher than the fast MA.
    def _params_constraints(self, params: typing.Dict) -> typing.Dict:
        if self.strategy == "obv":
            pass

        elif self.strategy == "sup_res":
            pass

        elif self.strategy == "rsi":
            pass

        elif self.strategy == "bb":
            pass

        elif self.strategy == "sma_sl_tp":
            params["slow_ma_period"] = max(params["slow_ma_period"], params["fast_ma_period"])
        
        elif self.strategy == "sma_sl_tp_fixed":
            params["slow_ma_period"] = max(params["slow_ma_period"], params["fast_ma_period"])

        elif self.strategy == "ichimoku":
            params["kijun"] = max(params["kijun"], params["tenkan"])

        elif self.strategy == "sma":
            params["slow_ma"] = max(params["slow_ma"], params["fast_ma"])

        elif self.strategy == "macd":
            params["ma_slow_period"] = max(params["ma_slow_period"], params["ma_fast_period"])

        elif self.strategy == "psar":
            params["initial_acc"] = min(params["initial_acc"], params["max_acc"])
            params["acc_increment"] = min(params["acc_increment"], params["max_acc"] - params["initial_acc"])

        return params


    def crowding_distance(self, population: typing.List[BacktestResult]) -> typing.List[BacktestResult]:
        
        for objective in ["pnl", "max_dd"]:

            population = sorted(population, key=lambda x:  getattr(x, objective))
            min_value = getattr(min(population, key=lambda x: getattr(x, objective)), objective)
            max_value = getattr(max(population, key=lambda x: getattr(x, objective)), objective)

            population[0].crowding_distance = float("inf")
            population[-1].crowding_distance = float("inf")

            for i in range(1, len(population) - 1):
                distance = getattr(population[i + 1], objective) - getattr(population[i - 1], objective)
                if max_value - min_value != 0:
                    distance = distance / (max_value - min_value)
                population[i].crowding_distance += distance
        
        return population



    def non_dominated_sortings(self, population: typing.Dict[int, BacktestResult]) -> typing.List[typing.List[BacktestResult]]:
        
        fronts = []

        for id_1, indiv_1 in population.items():
            for id_2, indiv_2 in population.items():
                if indiv_1.pnl >= indiv_2.pnl and indiv_1.max_dd <= indiv_2.max_dd \
                    and (indiv_1.pnl > indiv_2.pnl or indiv_1.max_dd < indiv_2.max_dd):
                    indiv_1.dominates.append(id_2)
                elif indiv_2.pnl >= indiv_1.pnl and indiv_2.max_dd <= indiv_1.max_dd \
                    and (indiv_2.pnl > indiv_1.pnl or indiv_2.max_dd < indiv_1.max_dd):
                    indiv_1.dominated_by += 1

            if indiv_1.dominated_by == 0:
                if len(fronts) == 0:
                    fronts.append([])
                fronts[0].append(indiv_1)
                indiv_1.rank = 0
        i = 0

        while True:

            fronts.append([])
            
            for indiv_1 in fronts[i]:
                for indiv_2_id in indiv_1.dominates:
                    population[indiv_2_id].dominated_by -= 1
                    if population[indiv_2_id].dominated_by == 0:
                        fronts[i + 1].append(population[indiv_2_id])
                        population[indiv_2_id].rank = i + 1

            if len(fronts[i + 1]) > 0:
                i += 1
            else:
                del fronts[-1]
                break
        return fronts


    def evaluate_population(self, population: typing.List[BacktestResult]) -> typing.List[BacktestResult]:
        
        if self.strategy == "obv":

            for bt in population:
                bt.pnl, bt.max_dd = strategies.obv.backtest(self.data, ma_period=bt.parameters["ma_period"])

                if bt.pnl == 0:
                    bt.pnl = -float("inf")
                    bt.max_dd = float("inf")

            return population

        elif self.strategy == "macd":

            with mp.Pool(mp.cpu_count()) as pool:
                results = pool.starmap(strategies.macd.backtest,
                                    ((self.data, bt.parameters["ma_fast_period"], bt.parameters["ma_slow_period"],
                                        bt.parameters["ma_signal_period"])
                                        for bt in population))
            for bt, (pnl, max_dd) in zip(population, results):
                bt.pnl, bt.max_dd = pnl, max_dd
                if bt.pnl == 0:
                    bt.pnl = -float("inf")
                    bt.max_dd = float("inf")
            return population

        elif self.strategy == "rsi":
                
            for bt in population:
                bt.pnl, bt.max_dd = strategies.rsi.backtest(self.data, rsi_period=bt.parameters["rsi_period"], ma_period=bt.parameters["ma_period"])

                if bt.pnl == 0:
                    bt.pnl = -float("inf")
                    bt.max_dd = float("inf")

            return population

        elif self.strategy == "bb":
                    
            for bt in population:
                bt.pnl, bt.max_dd = strategies.bb.backtest(self.data, ma_period=bt.parameters["ma_period"], std_multiplier=bt.parameters["std_multiplier"])

                if bt.pnl == 0:
                    bt.pnl = -float("inf")
                    bt.max_dd = float("inf")

            return population

        elif self.strategy == "ichimoku":
            with mp.Pool(mp.cpu_count()) as pool:
                results = pool.starmap(strategies.ichimoku.backtest,
                                    ((self.data, bt.parameters["tenkan"], bt.parameters["kijun"])
                                        for bt in population))
            for bt, (pnl, max_dd) in zip(population, results):
                bt.pnl, bt.max_dd = pnl, max_dd
                if bt.pnl == 0:
                    bt.pnl = -float("inf")
                    bt.max_dd = float("inf")
            return population

        elif self.strategy == "sma_sl_tp":
            with mp.Pool(mp.cpu_count()) as pool:
                results = pool.starmap(strategies.sma_sl_tp.backtest,
                                    ((self.data, bt.parameters["slow_ma_period"], 
                                    bt.parameters["fast_ma_period"], bt.parameters["atr_period"],
                                    bt.parameters["takeprofit"], bt.parameters["stoploss"])
                                        for bt in population))

            for bt, (pnl, max_dd) in zip(population, results):
                bt.pnl, bt.max_dd = pnl, max_dd
                if bt.pnl == 0:
                    bt.pnl = -float("inf")
                    bt.max_dd = float("inf")
            return population

        elif self.strategy == "sma_sl_tp_fixed":
            with mp.Pool(mp.cpu_count()) as pool:
                results = pool.starmap(strategies.sma_sl_tp_fixed.backtest,
                                    ((self.data, bt.parameters["slow_ma_period"], 
                                    bt.parameters["fast_ma_period"], bt.parameters["atr_period"],
                                    bt.parameters["takeprofit"], bt.parameters["stoploss"])
                                        for bt in population))

            for bt, (pnl, max_dd) in zip(population, results):
                bt.pnl, bt.max_dd = pnl, max_dd
                if bt.pnl == 0:
                    bt.pnl = -float("inf")
                    bt.max_dd = float("inf")
            return population

            # for bt in population:
            #     bt.pnl, bt.max_dd = strategies.ichimoku.backtest(self.data, tenkan_period=bt.parameters["tenkan"], kijun_period=bt.parameters["kijun"])

            #     if bt.pnl == 0:
            #         bt.pnl = -float("inf")
            #         bt.max_dd = float("inf")

            # return population

        elif self.strategy == "sup_res":

            with mp.Pool(mp.cpu_count()) as pool:
                results = pool.starmap(strategies.support_resistance.backtest,
                                    ((self.data, bt.parameters["min_points"], bt.parameters["min_diff_points"],
                                        bt.parameters["rounding_nb"], bt.parameters["take_profit"], bt.parameters["stop_loss"])
                                        for bt in population))
            for bt, (pnl, max_dd) in zip(population, results):
                bt.pnl, bt.max_dd = pnl, max_dd
                if bt.pnl == 0:
                    bt.pnl = -float("inf")
                    bt.max_dd = float("inf")
            return population

            # for bt in population:
            #     bt.pnl, bt.max_dd = strategies.support_resistance.backtest(self.data, min_points=bt.parameters["min_points"],
            #                                                 min_diff_points=bt.parameters["min_diff_points"],
            #                                                 rounding_nb=bt.parameters["rounding_nb"],
            #                                                 take_profit=bt.parameters["take_profit"], stop_loss=bt.parameters["stop_loss"])
            #     if bt.pnl == 0:
            #         bt.pnl = -float("inf")
            #         bt.max_dd = float("inf")

            # return population

        elif self.strategy == "sma":

            for bt in population:
                self.lib.Sma_execute_backtest(self.obj, bt.parameters["slow_ma"], bt.parameters["fast_ma"])
                bt.pnl = self.lib.Sma_get_pnl(self.obj)
                bt.max_dd = self.lib.Sma_get_max_dd(self.obj)

                if bt.pnl == 0:
                    bt.pnl = -float("inf")
                    bt.max_dd = float("inf")

            return population

        elif self.strategy == "psar":

            for bt in population:
                self.lib.Psar_execute_backtest(self.obj, bt.parameters["initial_acc"], bt.parameters["acc_increment"], bt.parameters["max_acc"])
                bt.pnl = self.lib.Psar_get_pnl(self.obj)
                bt.max_dd = self.lib.Psar_get_max_dd(self.obj)

                if bt.pnl == 0:
                    bt.pnl = -float("inf")
                    bt.max_dd = float("inf")

            return population
