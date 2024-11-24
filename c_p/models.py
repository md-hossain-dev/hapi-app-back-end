from django.db import models
from hapi_app.models import User,Wallet


class CPLevel(models.Model):
    level_name = models.CharField(max_length=100, null=True, blank=True,unique=True)
    level_up_coins = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.level_name} - {self.level_up_coins} coins"



class CoupleRelationship(models.Model):
    user1 = models.ForeignKey(User, related_name='user1_relationships', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='user2_relationships', on_delete=models.CASCADE)
    cp_level = models.ForeignKey(CPLevel, related_name='cp_level_relationships', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)  
    level_up = models.BooleanField(default=False)  

    def __str__(self):
        return f"Relationship: {self.user1.username} and {self.user2.username} ({self.cp_level.level_name})"


class RelationshipLog(models.Model):
    relationship = models.PositiveIntegerField()
    action = models.CharField(max_length=50)  # e.g., 'created', 'cancelled', 'coins_transferred'
    coins_transferred = models.PositiveIntegerField(default=0)  # Track coins transferred during actions
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Log: {self.action} - {self.coins_transferred} coins"



class RelationshipCancellation(models.Model):
    relationship = models.ForeignKey(CoupleRelationship, on_delete=models.CASCADE)
    cancelled_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cancelled_relationships')
    refunded_coins = models.PositiveIntegerField(default=0)  # Refund amount
    cancelled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cancelled: {self.relationship.user1.username} and {self.relationship.user2.username} - {self.refunded_coins} coins"

