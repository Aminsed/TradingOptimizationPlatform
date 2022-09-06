from typing import *
import logging

import requests
import json
import regex as re
import pandas as pd
from datetime import datetime


logger = logging.getLogger()


class DukascopyClient:
    def __init__(self):
        self._base_url = "https://freeserv.dukascopy.com/2.0/?path=api/historicalPrices&key=bsq3l3p5lc8w4s0c"
        self.symbols = self._get_symbols()

    def _make_request(self, endpoint: str, query_parameters: Dict):

        try:
            response = requests.get(self._base_url + endpoint, params=query_parameters)
        except Exception as e:
            logger.error("Connection error while making request to %s: %s", endpoint, e)
            return None

        if response.status_code == 200:
            return response.json()
        else:
            logger.error("Error while making request to %s: %s (status code = %s)",
                         endpoint, response.json(), response.status_code)
            return None

    def _get_symbols(self) -> List[str]:
            
        params = {
                'group': 'quotes',
                'method': 'realtimeSentimentIndex',
                'enabled': 'true',
                'type' : 'swfx',
                'jsonp' : '_callbacks____1kvynkpid',
                'key' : 'bsq3l3p5lc8w4s0c',
                }
        endpoint = "https://freeserv.dukascopy.com/2.0/api?"

        with requests.Session() as req:
            r = req.get(endpoint, params=params)
            text = r.text
            idx = text.index('(')
            text = text[idx+1:-1]
            raw_data = (json.loads(text))
            dataframe =  pd.DataFrame(raw_data)
            symbols = dataframe['id'].tolist()
            return symbols

    def get_historical_data(self, symbol: str, start_time: Optional[int] = None, end_time: Optional[int] = None):
            
        params = dict()

        params["instrument"] = symbol
        params["timeFrame"] = "1min"
        params["count"] = 5000
    
        if start_time is not None:
            params["start"] = int(start_time)
        if end_time is not None:
            params["end"] = int(end_time)
    
        endpoint = f"https://freeserv.dukascopy.com/2.0/?path=api/historicalPrices&key=bsq3l3p5lc8w4s0c"
        raw_candles = self._make_request(endpoint, params)['candles']
        candles = []

        if raw_candles is not None:
            for c in raw_candles:
                candles.append((float(c['timestamp']), float(c['bid_open']), float(c['bid_high']), float(c['bid_low']), float(c['bid_close']), float(c['bid_volume']),))
            return candles
        else:
            return None