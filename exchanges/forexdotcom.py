import requests
import json

class NewBrokerClient:
    def __init__(self, username, password, app_key):
        self._base_url = "https://ciapi.cityindex.com/v2"
        self._username = username
        self._password = password
        self._app_key = app_key
        self._session = self._login()

    def _login(self):
        endpoint = self._base_url + "/Session"
        data = {
            "Password": self._password,
            "AppVersion": "1",
            "AppComments": "",
            "UserName": self._username,
            "AppKey": self._app_key
        }
        response = requests.post(endpoint, json=data)
        if response.status_code == 200:
            session_data = response.json()
            session_token = session_data["Session"]
            return session_token
        else:
            raise Exception("Login failed")

    def _make_request(self, method, endpoint, params=None, data=None):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._session}"
        }
        url = self._base_url + endpoint
        response = requests.request(method, url, headers=headers, params=params, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Request failed with status code {response.status_code}")

    def get_cfd_markets(self, search_query, max_results=20):
        endpoint = "/cfd/markets"
        params = {
            "marketname": search_query,
            "maxresults": max_results,
            "ClientAccountId": self._username,
            "usemobileshortname": True
        }
        return self._make_request("GET", endpoint, params=params)

    # Implement other functionalities based on the broker's API documentation

# # Example usage
# client = NewBrokerClient("DM123456", "openthedoor", "ABC")
# markets = client.get_cfd_markets("GBP/USD", max_results=20)
# print(markets)
