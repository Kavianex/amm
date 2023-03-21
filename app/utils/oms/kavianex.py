import requests
import json

class KavianexRestAPI:
    def __init__(self, public, secret, main_net) -> None:
        if main_net:
            self.base = 'https://api.kavianex.com/api'
        else:
            self.base = 'https://api-testnet.kavianex.com/api'
        self.account_id = public
        self.token = secret
        self.name = "Kavianex"

    def get_header(self):
        return {
            "account-id": self.account_id, 
            "Authorization": self.token, 
            "Content-Type": "application/json",
        }

    def request(self, method, endpoint, params={}):
        base_url = self.base
        method = method.upper()
        url = base_url + endpoint 
        kwargs = {}
        if method == 'GET':
            kwargs['params'] = params
        else:
            kwargs['data'] = json.dumps(params)
        response = requests.request(method=method, url=url, headers=self.get_header(), **kwargs)
        if response.status_code >= 400:
            print(response.content)
        return response.json()

    # def get_orderbook(self, symbol, *args, **kwargs):
    #     result = self.request(method='GET', endpoint=f'/book/{symbol}', params={})
    #     return {'bids': result['bids'], 'asks': result['asks']}

    def get_open_orders(self, symbol, *args, **kwargs):
        result = self.request(method='GET', endpoint=f'/order/open/{self.account_id}/{symbol}', params={})
        return result

    def cancel_order(self, order_id, symbol=None, *args, **kwargs):
        result = self.request(method='DELETE', endpoint=f'/order/byId/{order_id}', params={})
        return result

    def send_order(self, order, *args, **kwargs):
        result = self.request(method='POST', endpoint=f'/order/', params=order)
        return result
