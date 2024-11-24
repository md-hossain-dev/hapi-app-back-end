from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
        blank=True
    )

    def __str__(self):
        return self.username





class Follower(models.Model):
    user = models.ForeignKey(
        User, 
        related_name='following', 
        on_delete=models.CASCADE  # When the user is deleted, their followers are also deleted
    )
    followed_user = models.ForeignKey(
        User, 
        related_name='followers', 
        on_delete=models.CASCADE  # When the followed user is deleted, the relationship is removed
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'followed_user')

    def __str__(self):
        return f'{self.user.username} follows {self.followed_user.username}'



class UserProfileVisit(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile_visit")
    visit_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.visit_count} visits"






class Invitation(models.Model):
    inviter = models.ForeignKey(User, related_name='sent_invitations', on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)  
    phone = models.CharField(max_length=15, null=True, blank=True)  
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(email__isnull=False) | models.Q(phone__isnull=False),
                name="email_or_phone_must_be_present"
            )
        ]

    def __str__(self):
        if self.email:
            return f"Invitation to {self.email} by {self.inviter.username}"
        return f"Invitation to {self.phone} by {self.inviter.username}"



class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    gold_coins = models.PositiveIntegerField(default=0)
    diamond_coins = models.PositiveIntegerField(default=0)

    def add_gold_coins(self, amount):
        self.gold_coins += amount
        self.save()

    def add_diamond_coins(self, amount):
        self.diamond_coins += amount
        self.save()

    def deduct_coins(self, amount):
        if self.gold_coins >= amount:
            self.gold_coins -= amount
            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.user.username} - Gold: {self.gold_coins}, Diamond: {self.diamond_coins}"



class WalletLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallet_logs')
    coins_amount = models.DecimalField(max_digits=12, decimal_places=2)
    action = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    wallet_description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Payment {self.user.username} - {self.action}"



class Image(models.Model):
    user = models.ForeignKey(User, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='user_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Image {self.id} uploaded by {self.user.username}"




class ChatRoom(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, related_name='created_rooms', on_delete=models.CASCADE)
    is_private = models.BooleanField(default=False)
    participants = models.ManyToManyField(User, through='RoomParticipant', related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class RoomParticipant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'room')


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    text = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender.username}: {self.text[:20]}'


class Game(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserGame(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)
    played_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.game.name} - {self.score}'





class CoinTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('BUY', 'Buy Coins'),
        ('GIFT', 'Gift Coins'),
        ('SELL', 'Sell Coins'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    usd_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    recipient = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='coin_transactions_received'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount} Coins"


class PaymentLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_logs')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_id = models.CharField(max_length=255)
    payment_status = models.CharField(max_length=50, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.payment_status}"


class GiftLog(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_gifts')
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='gift_logs_received'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} gifted {self.amount} Coins to {self.recipient.username}"
