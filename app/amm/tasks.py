from __future__ import absolute_import, unicode_literals
from celery import shared_task
from amm.mm import MarketMaker

@shared_task
def check_markets():
    return MarketMaker.check_markets()