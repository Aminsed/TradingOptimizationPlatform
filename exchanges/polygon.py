from typing import *
import logging
import requests
import datetime

logger = logging.getLogger()

class PolygonClient:
    def __init__(self):
        self.base_url = "https://api.polygon.io"
        self.api_key = 'mxpkpycUq3lprIQFLDP7c19jFsbpsWEc'
        self.symbols = self._get_symbols()

    def _make_request(self, endpoint, params=None):
        if params is None:
            params = {}
        params["apiKey"] = self.api_key
        url = f"{self.base_url}{endpoint}"

        print(f"Request URL: {url}")
        print(f"Request parameters: {params}")

        response = requests.get(url, params=params)

        try:
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error while making request to {endpoint}: {response.text} (status code = {response.status_code})")
                return None
        except ValueError as e:
            logger.error(f"Error parsing JSON response for {endpoint}: {e}")
            return None

    def _get_symbols(self) -> List[str]:
        endpoint = "/v3/reference/tickers"
        data = self._make_request(endpoint)

        if data is not None:
            symbols = [x["ticker"] for x in data["results"]]
            print(symbols)
            return symbols
        else:
            return []

    def get_historical_data(self, symbol: str, start_time: Optional[int] = None, end_time: Optional[int] = None):
        if start_time is not None:
            start_time = datetime.datetime.utcfromtimestamp(start_time / 1000).strftime('%Y-%m-%d')
        if end_time is not None:
            end_time = datetime.datetime.utcfromtimestamp(end_time / 1000).strftime('%Y-%m-%d')

        endpoint = f"/v2/aggs/ticker/{symbol}/range/1/minute"
        
        if start_time is not None and end_time is not None:
            endpoint += f"/{start_time}/{end_time}"
        elif start_time is not None:
            endpoint += f"/{start_time}/{start_time}"
        elif end_time is not None:
            endpoint += f"/{end_time}/{end_time}"

        params = {"limit": 50000}  # Add the limit parameter here
        raw_candles = self._make_request(endpoint, params)

        candles = []

        if raw_candles is not None and raw_candles["results"]:
            for c in raw_candles["results"]:
                candles.append((c["t"], c["o"], c["h"], c["l"], c["c"], c["v"]))
            return candles
        else:
            return None
