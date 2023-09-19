import requests
import json
import logging

logger = logging.getLogger()

class GCapiClient:
    def __init__(self, username, password, appkey):
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

    def get_historical_data(self, symbol: str, start_time: Optional[int] = None, end_time: Optional[int] = None):
        # Get market_id from symbol
        market_info = self.get_market_info(symbol)
        try:
            market_id = market_info['Markets'][0]['MarketId']
        except (KeyError, IndexError):
            return None

        # If start_time and end_time are not provided, get the last 5000 bars
        if start_time is None or end_time is None:
            num_ticks = 5000
            endpoint = f'/market/{market_id}/barhistory?PriceBars={num_ticks}'
            return self._make_request(endpoint)

        # If start_time and end_time are provided, get historical data between these timestamps
        else:
            params = {
                'fromTimeStampUTC': start_time,
                'toTimestampUTC': end_time,
                'maxResults': 4000
            }
            endpoint = f'/market/{market_id}/tickhistorybetween'
            return self._make_request(endpoint, params)
