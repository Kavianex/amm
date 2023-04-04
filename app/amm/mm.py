from amm import models
from utils import enums
import time

class MarketMaker:
    def __init__(self, strategy) -> None:
        self.strategy = strategy
    
    def check_market(self):
        maker_orders = self.get_maker_orders()
        bids = {order['price']: order for order in maker_orders if order['side']== enums.OrderSide.long.value} 
        asks = {order['price']: order for order in maker_orders if order['side']== enums.OrderSide.short.value} 
        canceling_orders, new_orders = self.get_balancing_orders(bids, asks)
        self.rebalance_orders(canceling_orders=canceling_orders, new_orders=new_orders)

    def rebalance_orders(self, canceling_orders, new_orders):
        new_order_idx = 0
        self.strategy.maker.client.cancel_all_symbol_orders(self.strategy.symbol)
        # for canceling_order in canceling_orders:
        #     self.cancel_order(canceling_order)
        #     time.sleep(0.5)
            # if new_orders[new_order_idx:]:
            #     self.send_order(new_orders[new_order_idx])
            #     new_order_idx += 1
        for new_order in new_orders[new_order_idx:]:
            self.send_order(new_order)
            time.sleep(0.5)

    
    def get_balancing_orders(self,bids, asks):
        canceling_orders = []
        # open_orders = self.get_open_orders()
        # for open_order in open_orders:
        #     open_order_price = open_order['price']
        #     if open_order['side'] == enums.OrderSide.long.value:
        #         if open_order_price not in bids:
        #             canceling_orders.append(open_order)
        #         else:
        #             del bids[open_order_price]
        #     else:
        #         if open_order_price not in asks:
        #             canceling_orders.append(open_order)
        #         else:
        #             del asks[open_order_price]
        new_orders = list(bids.values()) + list(asks.values())
        return canceling_orders, new_orders

    def send_order(self, order):
        result = self.strategy.maker.client.send_order(order)
        print(result)

    def cancel_order(self, order):
        open_orders = self.strategy.maker.client.cancel_order(order['id'])
        return open_orders

    def get_open_orders(self):
        open_orders = self.strategy.maker.client.get_open_orders(self.strategy.symbol)
        return open_orders
    
    def get_maker_orders(self):
        last_price = self.strategy.taker.client.get_last_price(self.strategy.symbol)
        last_price = int(last_price)
        maker_orders = []
        order_value = 1000
        for i in range(1, 5):
            for side in [enums.OrderSide.long.value, enums.OrderSide.short.value]:
                price = last_price + (i if side == enums.OrderSide.short.value else -i)
                quantity = order_value / price
                quantity = int(quantity * 1000) / 1000
                maker_orders.append({
                    "price": price,
                    "side": side,
                    "type": enums.OrderType.limit.value,
                    "symbol": self.strategy.symbol,
                    "quantity": quantity
                })
        return maker_orders
        
        
    @classmethod
    def check_markets(cls):
        strategies = cls.get_strategies()
        for strategy in strategies:
            mm = cls(strategy=strategy)
            mm.check_market()

    @classmethod
    def get_strategies(cls):
        strategies = models.Strategy.objects.filter(active=True)
        return strategies
