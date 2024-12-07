from django.db import models
from hapi_app.models import User


class RechargeCoin(models.Model):
    coins = models.PositiveIntegerField()
    bonus_coins = models.PositiveIntegerField(default=0)
    total_coins = models.PositiveIntegerField(default=0,null=True,blank=True) 
    amount = models.DecimalField(max_digits=10, decimal_places=2) 
    created_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        # Automatically calculate total_coins
        self.total_coins = self.coins + self.bonus_coins
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Recharge: {self.coins} coins (+{self.bonus_coins} bonus)"


class ExchangeDiamondToCoin(models.Model):
    diamond = models.PositiveIntegerField()
    exchange_coin = models.PositiveIntegerField() 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return  self.bonus_coins


class CoinPurchaseRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="purchase_requests")
    recharge_coin = models.ForeignKey(RechargeCoin, on_delete=models.CASCADE, related_name="purchase_requests")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request by {self.user.username}: {self.recharge_coin.total_coins} coins ({self.status})"