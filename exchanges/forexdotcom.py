import requests
import json
import logging
from typing import Optional

logger = logging.getLogger()


class GCapiException(Exception):
    def __init__(self, exception):
        self.exception = exception

    def get_exception(self):
        return self.exception

    def get_error_message(self):
        if self.exception['ErrorMessage']:
            return self.exception['ErrorMessage']

    def get_status_code(self):
        if self.exception['StatusCode']:
            return self.exception['StatusCode']

    def get_additional_info(self):
        if self.exception['AdditionalInfo']:
            return self.exception['AdditionalInfo']

    def get_http_status(self):
        if self.exception['HttpStatus']:
            return self.exception['HttpStatus']

    def get_error_code(self):
        if self.exception['ErrorCode']:
            return self.exception['ErrorCode']


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
        if start_time is not None and end_time is not None:
            r = self._session.get(
                self._base_url + f'/market/{symbol}/tickhistorybetween?fromTimeStampUTC={start_time}&toTimestampUTC={end_time}&priceType=MID')
        else:
            r = self._session.get(self._base_url + f'/market/{symbol}/tickhistory?PriceTicks=5000&priceType=MID')
        resp = json.loads(r.text)
        prices = []
        try:
            for price in resp['PriceTicks']:
                # Extract timestamp from the string and convert it to float
                timestamp = float(price['TickDate'][6:-2]) / 1000
                # Append tuple (timestamp, price, price, price, price, volume)
                prices.append((timestamp, price['Price'], price['Price'], price['Price'], price['Price'], 0))
            return prices
        except:
            raise GCapiException(resp)

