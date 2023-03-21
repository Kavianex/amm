from enum import Enum as BaseEnum

class Enum(BaseEnum):
    @classmethod
    def choices(cls):
        _choices = tuple()
        for item in cls.__members__.values():
            _choices = _choices + ((item.value, item.name),)
        return _choices

class ExchangeName(Enum):
    kavianex = "KAVIANEX"
    binance = "BINANCE"

class OrderType(Enum):
    market = 'MARKET'
    limit = "LIMIT"

class OrderStatus(Enum):
    pending = 'PENDING'
    done = "DONE"
    new = "NEW"
    cancel = "CANCELED"
    failed = "FAILED"

class OrderSide(Enum):
    buy = 'BUY'
    sell = 'SELL'
    long = 'LONG'
    short = 'SHORT'

