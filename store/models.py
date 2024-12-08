from django.db import models
from hapi_app.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

        
    
class Product(models.Model):
    name = models.CharField(max_length=100,unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='products/')
    day = models.PositiveIntegerField()
    star = models.PositiveIntegerField(blank=True, null=True)
    price = models.PositiveIntegerField()  # Price in coins
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions_user')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    coins_spent = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.user.username} purchased {self.product.name}'

    class Meta:
        ordering = ['-timestamp']



class Gift(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_sent_gifts')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_received_gifts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.sender.username} sent a gift to {self.receiver.username}'