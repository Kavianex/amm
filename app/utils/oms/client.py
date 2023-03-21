from utils.oms.binance import BinanceFuturesUsdt
from utils.oms.kavianex import KavianexRestAPI
from utils import enums


class OmsClient:
    def __init__(self, exchange_obj) -> None:
        if exchange_obj.name == enums.ExchangeName.kavianex.value:
            self.exchange = KavianexRestAPI(
                public=exchange_obj.api_key, 
                secret=exchange_obj.secret_key, 
                main_net=exchange_obj.main_net,
                )
        elif exchange_obj.name == enums.ExchangeName.binance.value:
            self.exchange = BinanceFuturesUsdt(
                public=exchange_obj.api_key, 
                secret=exchange_obj.secret_key, 
                main_net=exchange_obj.main_net,
                )
        else:
            raise Exception(f"Invalid Exchange: {exchange_obj.name}")

    def get_orderbook(self, symbol, *args, **kwargs):
        return self.exchange.get_orderbook(symbol, *args, **kwargs)

    def get_last_price(self, symbol, *args, **kwargs):
        return self.exchange.get_last_price(symbol, *args, **kwargs)

    def cancel_order(self, order_id, symbol=None, *args, **kwargs):
        return self.exchange.cancel_order(order_id, symbol, *args, **kwargs)
 
    def cancel_all_symbol_orders(self, symbol, *args, **kwargs):
        return self.exchange.cancel_all_symbol_orders(symbol, *args, **kwargs)


    def send_order(self, order, *args, **kwargs):
        return self.exchange.send_order(order, *args, **kwargs)

    def get_open_orders(self, symbol, *args, **kwargs):
        return self.exchange.get_open_orders(symbol, *args, **kwargs)

