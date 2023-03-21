from django.contrib import admin, messages
from amm import models, tasks


class ExchangeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'main_net']

def check_markets(modeladmin, request, queryset):
    msg = 'All market checks'
    tasks.check_markets.delay()
    messages.success(request, msg)
check_markets.short_description = "Check markets"
class StrategyAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'maker', 'taker']
    actions = [check_markets,]





admin.site.register(models.Exchange, ExchangeAdmin)
admin.site.register(models.Strategy, StrategyAdmin)
