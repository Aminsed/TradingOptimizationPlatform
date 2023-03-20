from typing import *
import logging
import time

import numpy as np
import pandas as pd
from influxdb import InfluxDBClient

logger = logging.getLogger()


class InfluxDBClientWrapper:
    def __init__(self, exchange: str):
        self.client = InfluxDBClient(host='localhost', port=8086)
        self.exchange = exchange
        self.client.create_database(exchange)
        self.client.switch_database(exchange)

    def write_data(self, symbol: str, data: List[Tuple]):

        min_ts, max_ts = self.get_first_last_timestamp(symbol)

        if min_ts is None:
            min_ts = float("inf")
            max_ts = 0

        filtered_data = []

        for d in data:
            if d[0] < min_ts:
                filtered_data.append(d)
            elif d[0] > max_ts:
                filtered_data.append(d)

        if len(filtered_data) == 0:
            logger.warning("%s: No data to insert", symbol)
            return

        points = []

        for d in filtered_data:
            point = {
                "measurement": symbol,
                "time": int(d[0]),
                "fields": {
                    "open": d[1],
                    "high": d[2],
                    "low": d[3],
                    "close": d[4],
                    "volume": d[5]
                }
            }
            points.append(point)

        self.client.write_points(points)

    def get_data(self, symbol: str, from_time: int, to_time: int) -> Union[None, pd.DataFrame]:

        start_query = time.time()

        query = f"SELECT * FROM {symbol} WHERE time >= {from_time}ms AND time <= {to_time}ms"
        result = self.client.query(query)

        if len(result) == 0:
            return None

        df = pd.DataFrame(result[symbol])

        df["time"] = pd.to_datetime(df["time"].values.astype(np.int64), unit="ms")
        df.set_index("time", drop=True, inplace=True)

        query_time = round((time.time() - start_query), 2)

        logger.info("Retrieved %s %s data from database in %s seconds", len(df.index), symbol, query_time)

        return df

    def get_first_last_timestamp(self, symbol: str) -> Union[Tuple[None, None], Tuple[float, float]]:

        query_first = f"SELECT first(open) FROM {symbol}"
        query_last = f"SELECT last(open) FROM {symbol}"

        result_first = self.client.query(query_first)
        result_last = self.client.query(query_last)

        if len(result_first) == 0 or len(result_last) == 0:
            return None, None

        first_ts = pd.to_datetime(list(result_first.get_points())[0]['time']).timestamp() * 1000
        last_ts = pd.to_datetime(list(result_last.get_points())[0]['time']).timestamp() * 1000

        return first_ts, last_ts
