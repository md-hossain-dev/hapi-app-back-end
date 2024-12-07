from django.urls import path
from .views import RechargeCoinAPIView,CreateRechargeCoinAPIView, CoinPurchaseRequestCreateView,CoinPurchaseRequestUpdateView, ExchangeDiamondToCoinAPIView, CreateExchangeDiamondToCoinAPIView

urlpatterns = [
    path('recharge-coin/', RechargeCoinAPIView.as_view(), name='recharge-coin-api'),
    path('create-recharge-coin/', CreateRechargeCoinAPIView.as_view(), name='create-recharge-coin-api'),
    path('exchange-diamond-to-coin/', ExchangeDiamondToCoinAPIView.as_view(), name='exchange-diamond-to-coin-api'),
    path('create-exchange-diamond-to-coin/', CreateExchangeDiamondToCoinAPIView.as_view(), name='create-exchange-diamond-to-coin-api'),
    path('coin-purchase-request/', CoinPurchaseRequestCreateView.as_view(), name='coin_purchase_request'),
    path('coin-purchase-accepted-and-rejected/', CoinPurchaseRequestUpdateView.as_view(), name='coin-purchase-accepted-and-rejected'),
]
