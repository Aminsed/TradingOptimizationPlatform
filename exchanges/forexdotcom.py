import requests
import logging

logger = logging.getLogger()

class CityIndexClient:
    def __init__(self, username, password, app_key, client_account_id):
        self._base_url = "https://ciapi.cityindex.com"
        self.username = username
        self.password = password
        self.app_key = app_key
        self.client_account_id = client_account_id
        self._session = self._login()
        self.symbols = self._get_symbols()

    def _make_request(self, endpoint: str, params: dict = None, method: str = 'GET', json: dict = None):
        url = self._base_url + endpoint
        try:
            if method == 'GET':
                response = requests.get(url, params=params)
            elif method == 'POST':
                response = requests.post(url, json=json)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error("Request failed: %s", response.json())
                return None
        except Exception as e:
            logger.error("Connection error: %s", e)
            return None

    def _login(self):
        login_endpoint = "/v2/Session"
        login_data = {
            "UserName": self.username,
            "Password": self.password,
            "AppKey": self.app_key,
            "AppVersion": "1",
            "AppComments": ""
        }
        response = self._make_request(login_endpoint, method='POST', json=login_data)
        if response is not None:
            return response["Session"]
        else:
            return None

    def _get_symbols(self):
        market_endpoint = "/TradingAPI/spread/markets"
        market_params = {
            "ClientAccountId": self.client_account_id,
            "maxresults": 500
        }
        markets = self._make_request(market_endpoint, params=market_params)
        if markets is not None:
            symbols = {market['MarketName']: market['MarketId'] for market in markets['Markets']}
            return symbols
        else:
            return None
            
    def get_historical_data(self, symbol, start_time=None, end_time=None, interval="HOUR", span=1, max_results=1000):
        # Look up the market ID for the given symbol
        market_id = self.symbols.get(symbol)
        if market_id is None:
            logger.error("Symbol not found: %s", symbol)
            return None

        historical_data_endpoint = f"/TradingAPI/market/{market_id}/barhistorybetween"
        historical_data_params = {
            "interval": interval,
            "span": span,
            "fromTimestampUTC": start_time,
            "toTimestampUTC": end_time,
            "maxResults": max_results
        }
        historical_data = self._make_request(historical_data_endpoint, params=historical_data_params)
        if historical_data is not None:
            candles = []
            for bar in historical_data['PriceBars']:
                # Convert times from "/Date(x)/" format to epoch time
                timestamp = int(bar['BarDate'][6:-2]) / 1000
                candles.append((timestamp, bar['Open'], bar['High'], bar['Low'], bar['Close'], bar['Volume']))
            return candles
        else:
            return None