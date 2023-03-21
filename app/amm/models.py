from django.db import models
from django.utils import timezone
from utils import enums
from utils.oms.client import OmsClient


class Exchange(models.Model):
    name = models.CharField(choices=enums.ExchangeName.choices(), max_length=20)
    remark = models.CharField(default="", max_length=50, blank=True, null=True)
    api_key = models.CharField(default="", max_length=70, blank=True, null=True)
    secret_key = models.CharField(default="", max_length=200, blank=True, null=True)
    main_net = models.BooleanField(default=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        return super(Exchange, self).save(*args, **kwargs)

    def is_valid(self):
        pass

    def __str__(self) -> str:
        return self.name
    
    @property
    def client(self):
        return OmsClient(self)
    
class Strategy(models.Model):
    maker = models.ForeignKey(Exchange, on_delete=models.CASCADE, null=True, blank=True, related_name='maker_exchange')
    taker = models.ForeignKey(Exchange, on_delete=models.CASCADE, null=True, blank=True, related_name='taker_exchange')
    symbol = models.CharField(default='BTCUSDT', max_length=10, null=True, blank=True)
    active = models.BooleanField(default=True, null=True, blank=True)


class Order(models.Model):
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE, null=True, blank=True)
    side = models.CharField(default=enums.OrderSide.buy.value, max_length=20, null=True, blank=True)
    symbol = models.CharField(default="", max_length=20, null=True, blank=True)
    base = models.CharField(default="", max_length=20, null=True, blank=True)
    quote = models.CharField(default="", max_length=20, null=True, blank=True)
    quantity = models.FloatField(default=0, null=True, blank=True)
    quote_value = models.FloatField(default=0, null=True, blank=True)
    order_type = models.CharField(default=enums.OrderType.market.value, max_length=20, null=True, blank=True)
    order_id = models.CharField(default="", max_length=46, null=True, blank=True)
    client_id = models.CharField(default="", max_length=46, null=True, blank=True)
    price = models.FloatField(default=0, null=True, blank=True)
    stop_price = models.FloatField(default=0, null=True, blank=True)
    stop_limit_price = models.FloatField(default=0, null=True, blank=True)
    filled_quote = models.FloatField(default=0, null=True, blank=True)
    filled_base = models.FloatField(default=0, null=True, blank=True)
    status = models.CharField(default=enums.OrderStatus.new.value, max_length=20, null=True, blank=True)
    description = models.TextField(default="", null=True, blank=True)

    insert_time = models.DateTimeField(default=timezone.now, null=True, blank=True)
    update_time = models.DateTimeField(default=timezone.now, null=True, blank=True)
