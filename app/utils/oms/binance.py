import requests
import hashlib
import time
import math
import urllib
import hmac
import json
import base64
import websocket
import json
import threading
import time
from utils import enums

class BinanceFuturesUsdt:
    def __init__(self, public, secret, main_net):
        if main_net:
            self.base = 'https://fapi.binance.com'
        else:
            self.base = 'https://testnet.binancefuture.com'
        self.public = public
        self.secret = secret
        self.name = "BinanceFuturesUsdt"
    
    def get_header(self):
        return {"X-MBX-APIKEY": self.public, "Content-Type": "application/json"}

    def sign(self, params):
        params['timestamp'] = (int(time.time()) * 1000)
        params['recvWindow'] = 50000
        params_str = urllib.parse.urlencode(params).encode('utf-8')
        sign = hmac.new(
            key=str.encode(self.secret),
            msg=params_str,
            digestmod=hashlib.sha256
        ).hexdigest()
        return params_str.decode("utf-8") + "&signature=" + str(sign)

    def request(self, method, endpoint, params={}):
        base_url = self.base
        url = base_url + endpoint + '?' + self.sign(params=params)
        response = requests.request(method=method.upper(), url=url, headers=self.get_header())
        return response.json()

    def get_orderbook(self, symbol, *args, **kwargs):
        params = {
            'limit': 50,
            'symbol': symbol,
        }
        result = self.request(method='GET', endpoint='/fapi/v1/depth', params=params)
        return {'bids': result['bids'], 'asks': result['asks']}

    def filter_params(self, symbol, quantity=0, price=0):
        qty = float(quantity)
        price = float(price)
        lot = {}
        tick = {}
        for fil in self.get_symbol_info(symbol=symbol)['filters']:
            if fil['filterType'] == 'LOT_SIZE':
                lot = fil
            elif fil['filterType'] == 'PRICE_FILTER':
                tick = fil
        min_qty = float(lot['minQty'])
        max_qty = float(lot['maxQty'])
        step_size = float(lot['stepSize'])
        if qty <= min_qty:
            qty = min_qty
        elif qty >= max_qty:
            qty = max_qty
        else:
            steps = int(qty / step_size)
            qty = steps * step_size
        base_asset_precision = self.get_symbol_info(symbol=symbol)['quantityPrecision']
        qty = ('{:.' + str(base_asset_precision) + 'f}').format(qty)

        min_price = float(tick['minPrice'])
        max_price = float(tick['maxPrice'])
        tick_size = float(tick['tickSize'])
        if price <= min_price:
            price = min_price
        elif price >= max_price:
            price = max_price
        else:
            steps = int(price / tick_size)
            price = steps * tick_size
        quote_asset_precision = self.get_symbol_info(symbol=symbol)['pricePrecision']
        price = ('{:.' + str(quote_asset_precision) + 'f}').format(price)
        return {"price": price, "quantity": qty}

    def send_order(self, params, *args, **kwargs):
        filtered_params = self.filter_params(symbol=params['symbol'], quantity=params.get('quantity', 0),
                                             price=params.get('stop_price', 0))
        filtered_quantity = filtered_params['quantity']
        filtered_stop_price = filtered_params['price']
        filtered_price = 0
        client_id = params['client_id']
        order = {
            'symbol': params['symbol'],
            'quantity': filtered_quantity,
            'stopPrice': filtered_stop_price,
            'side': params['side'],
            "type": params["type"],
            "newClientOrderId": client_id,
        }
        # if order["type"] == enums.OrderType.stop_market.value:
        #     order["type"] = "STOP_LOSS"
        endpoint = f"/fapi/v1/order"
        response = self.request(method="POST", endpoint=endpoint, params=order)
        if 'orderId' not in response:
            return {}
        response_status = enums.OrderStatus.new.value
        result = {
            'quantity': filtered_quantity,
            'stop_price': filtered_stop_price,
            'price': filtered_price,
            "client_id": client_id,
            "orderId": response["orderId"],
            "status": response_status,
        }
        return result

    def cancel_order(self, symbol, order_id=None, *args, **kwargs):
        params = {'symbol': symbol, 'orderId': int(order_id)}
        result = self.request(method="DELETE", endpoint='/fapi/v1/order', params=params)
        if result.get("status", "") == "CANCELED":
            return True
        return False

    def account_info(self):
        response = self.request('GET', endpoint='/fapi/v2/account')
        response["balances"] = []
        for asset_info in response['assets']:
            free = float(asset_info['availableBalance'])
            locked = float(asset_info['initialMargin'])
            asset_pnl = float(asset_info['unrealizedProfit'])
            if free > 0 or locked > 0:
                response['balances'].append({
                    "asset": asset_info['asset'],
                    "free": free,
                    "locked": locked + asset_pnl
                })
        positions = []
        for position in response['positions']:
            position_quantity = float(position['positionAmt'])
            if position_quantity == 0:
                continue
            positions.append(position)
        response["positions"] = positions
        response["pnl"] = 0
        return response

    def get_nav(self, assets):
        nav = 0
        prices = self.get_prices_for_nav(list(set([asset['symbol'] for asset in assets])))
        for asset in assets:
            amount = (asset['free'] + asset['locked'])
            price = prices[asset['symbol']]
            nav += amount * price
        return nav

    def get_prices_for_nav(self, assets):
        data = {}
        for asset in assets:
            if asset != 'USDT':
                price = self.get_last_price(asset + 'USDT')
                if price > 0:
                    data[asset] = price
                else:
                    price_btc = self.get_last_price(asset + 'BTC')
                    data[asset] = price_btc * self.get_last_price('BTCUSDT')
            else:
                data['USDT'] = 1
        return data

    def get_last_price(self, symbol, *args, **kwargs):
        # TODO: use self.request
        try:
            # ticker = redis.hget(self.name + '-LASTPRICE', symbol)
            # if ticker['time'] > int(time.time()) - 30:
            #     return ticker['price']
            raise Exception('lastprice expired ' + symbol)
        except Exception as e:
            tickers = requests.get(f'{self.base}/fapi/v1/ticker/price').json()
            found = False
            last_price = 0
            for ticker in tickers:
                # redis.hset(self.name + '-LASTPRICE', ticker['symbol'],
                #            json.dumps({'price': float(ticker['price']), 'time': int(time.time())}))
                if ticker['symbol'] == symbol:
                    found = True
                    last_price = float(ticker['price'])
            if not found:
                try:
                    ticker = requests.get(f'{self.base}/api/v3/ticker/price?symbol={symbol}').json()
                    # redis.hset(self.name + '-LASTPRICE', ticker['symbol'],
                    #            json.dumps({'price': float(ticker['price']), 'time': int(time.time())}))
                    last_price = float(ticker['price'])
                except Exception as e:
                    last_price = 0
            return last_price

    def get_symbol_info(self, symbol):
        symbol = symbol.upper()
        info = self.set_symbols_info(symbol=symbol)
        return info

    def set_symbols_info(self, symbol):
        exchange_info = requests.get(self.base + '/fapi/v1/exchangeInfo').json()
        info = {}
        for symbol_info in exchange_info['symbols']:
            # redis.hset(self.name + '-exchangeInfo', symbol_info['symbol'], json.dumps(symbol_info))
            if symbol and symbol_info['symbol'] == symbol:
                info = symbol_info
        return info

    def get_all_price(self):
        response = requests.get(self.base + '/fapi/v1/ticker/price').json()
        data = {}
        for info in response:
            data[info["symbol"]] = float(info["price"])
        return data

    def open_positions(self, symbol):
        params = {
            # "symbol": symbol
        }
        result = self.request(method="GET", endpoint="/fapi/v2/positionRisk", params=params)
        position = {}
        for open_position in result:
            if open_position['symbol'] == symbol:
                position_quantity = float(open_position["positionAmt"])
                if not position_quantity == 0:
                    if open_position['positionSide'] == "BOTH":
                        position = open_position
                        position["quantity"] = abs(position_quantity)
                        position["price"] = float(position["entryPrice"])
                        position["leverage"] = float(position["leverage"])
                        position[
                            "side"] = enums.OrderSide.buy.value if position_quantity > 0 else enums.OrderSide.sell.value
        return position
        # if not len(result) == 1:
        #     return {}
        # position = result[0]
        # if not position["positionSide"] == "BOTH":
        #     return {}
        # position_quantity = float(position["positionAmt"])
        # if position_quantity == 0:
        #     return {}
        # position["quantity"] = abs(position_quantity)
        # position["price"] = float(position["entryPrice"])
        # position["leverage"] = float(position["leverage"])
        # position["side"] = enums.OrderSide.buy.value if position_quantity > 0 else enums.OrderSide.sell.value
        # return position

    def cancel_stop_orders(self, orders):
        for order in orders:
            self.cancel_order(symbol=order['symbol'], order_id=order['order_id'])
        return True



class BinanceFuturesUSDTWebsocket:

    def __init__(self, public, main_net, call_back, *args, **kwargs):
        if main_net:
            self.base = "wss://fstream.binance.com"
        else:
            self.base = "wss://stream.binancefuture.com"
        self.name = 'BINANCE-Futures@USDT'
        self.status = 'ACTIVE'
        self.public = public
        self.listen_key = ''
        self.ws = None
        self.call_back = call_back
        self.get_listen_key()

    def get_listen_key(self):
        url = f"{self.base}/fapi/v1/listenKey"
        headers = {
            'X-MBX-APIKEY': self.public
        }

        response = requests.post(url, headers=headers)
        self.listen_key = response.json()['listenKey']
        return self.listen_key

    def update_listen_key(self):
        print('updating listen key:', self.public)
        if self.status == 'STOP':
            return 0
        url = f"{self.base}/fapi/v1/listenKey?listenKey={self.listen_key}"
        headers = {
            'X-MBX-APIKEY': self.public
        }

        response = requests.put(url, headers=headers)
        return response.json()

    def stop(self):
        self.status = 'STOP'

    def call_order(self, new_order, t=0):
        data = {"order": new_order}
        self.call_back(data)


    def stream(self):
        def on_close(ws):
            print("connection closed")
            try:
                ws.close()
            except Exception as e:
                pass
            if self.status == 'STOP':
                return False
            self.stream()

        def on_message(ws, msg):
            try:
                data = json.loads(msg)
                print(data)
                if 'e' in data:
                    if data['e'] == 'ORDER_TRADE_UPDATE':
                        self.call_order(data['o'])
            except Exception as e:
                print(e)

        def on_open(ws):
            print("streamer opened for", self.public)

        def on_error(ws, err):
            print(err)

        websocket.enableTrace(False)
        print(f"{self.name} OPENING")
        url = f'{self.base}/ws/{self.listen_key}'
        ws = websocket.WebSocketApp(url=url,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close,
                                    on_open=on_open,
                                    )
        self.ws = ws
        ws.run_forever()

    def streamer(self):
        thread = threading.Thread(target=self.stream)
        thread.start()

    def ping(self):
        self.update_listen_key()

