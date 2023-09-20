import requests
import json
import logging
import configparser
import os

from typing import Optional

logger = logging.getLogger()

class GCapiClient:
    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        config_path = os.path.join(dir_path, 'config.ini')
        config = configparser.ConfigParser()
        config.read(config_path)
        
        username = config['Credentials']['username']
        password = config['Credentials']['password']
        appkey = config['Credentials']['appkey']
        self._base_url = "https://ciapi.cityindex.com/TradingAPI"
        self._session = self._create_session(username, password, appkey)

    def _create_session(self, username, password, appkey):
        headers = {'Content-Type': 'application/json'}
        data = {
            "UserName": username,
            "Password": password,
            "AppKey": appkey
        }
        try:
            response = requests.post(self._base_url + '/session', headers=headers, json=data)
            response.raise_for_status()
            resp = response.json()
            if resp['StatusCode'] != 1:
                raise Exception(resp)
            session = resp['Session']
            headers = {
                'Content-Type': 'application/json',
                'UserName': username,
                'Session': session
            }
            s = requests.Session()
            s.headers = headers
            return s
        except Exception as e:
            logger.error("Error while creating session: %s", e)
            return None

    def _make_request(self, endpoint: str, query_parameters: dict = None):
        if query_parameters is None:
            query_parameters = {}
        try:
            response = self._session.get(self._base_url + endpoint, params=query_parameters)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Error while making request to %s: %s", endpoint, e)
            return None

    def get_market_info(self, market_name):
        endpoint = f'/cfd/markets?MarketName={market_name}'
        return self._make_request(endpoint)

    def get_prices(self, market_id, num_ticks=1, price_type='MID'):
        endpoint = f'/market/{market_id}/tickhistory?PriceTicks={num_ticks}&priceType={price_type}'
        return self._make_request(endpoint)

        def get_historical_data(self, market_id: str, num_ticks: int = 4000, start_time: Optional[int] = None, end_time: Optional[int] = None):
            interval = "MINUTE"
            span = 1

            # Convert timestamps to Gain Capital's expected format
            if start_time is not None:
                start_time = int(start_time / 1000)
            if end_time is not None:
                end_time = int(end_time / 1000)

            # If only end_time is provided, use the barhistorybefore endpoint
            if end_time is not None and start_time is None:
                r = self._session.get(
                    self._base_url + f'/market/{market_id}/barhistorybefore?interval={interval}&span={span}&maxResults={num_ticks}&toTimeStampUTC={end_time}')
            elif start_time is not None:
                r = self._session.get(
                    self._base_url + f'/market/{market_id}/barhistoryafter?interval={interval}&span={span}&maxResults={num_ticks}&fromTimeStampUTC={start_time}')
            else:
                # Default to the barhistory endpoint if no specific timestamps are provided
                r = self._session.get(self._base_url + f'/market/{market_id}/barhistory?interval={interval}&span={span}&PriceBars={num_ticks}')

            resp = json.loads(r.text)
            prices = []

            try:
                if 'PriceBars' in resp:
                    for price in resp['PriceBars']:
                        # Extract timestamp from the string and convert it to float
                        timestamp = float(price['BarDate'][6:-2])
                        
                        # Check if 'Volume' key exists, if not set it to 0
                        volume = price.get('Volume', 0)
                        # Append tuple (timestamp, open, high, low, close, volume)
                        prices.append((timestamp, price['Open'], price['High'], price['Low'], price['Close'], volume))
                return prices
            except:
                raise GCapiException(resp)
