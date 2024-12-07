from rest_framework import serializers
from .models import RechargeCoin, ExchangeDiamondToCoin,CoinPurchaseRequest

class RechargeCoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = RechargeCoin
        fields = '__all__'
        # read_only_fields = ('total_coins')


class ExchangeDiamondToCoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeDiamondToCoin
        fields = '__all__'


class CoinPurchaseRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinPurchaseRequest
        fields = '__all__'
        read_only_fields = ('status', 'total_coins', 'user')