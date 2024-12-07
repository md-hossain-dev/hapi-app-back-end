from django.contrib import admin
from .models import RechargeCoin,ExchangeDiamondToCoin,CoinPurchaseRequest

admin.site.register(RechargeCoin)
admin.site.register(ExchangeDiamondToCoin)
admin.site.register(CoinPurchaseRequest)
