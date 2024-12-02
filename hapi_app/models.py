from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class UserLV(models.Model):
    level_name = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.level_name



class Country(models.Model):
    name = models.CharField(max_length=54, unique=True)
    short_code = models.CharField(max_length=20, unique=True)
    county_flag = models.ImageField(upload_to='county_flag/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class User(AbstractUser):
    GENDER_CHOICES = (
        ('male', 'male'),
        ('female', 'female'),
        ('others', 'others'),
    )
    email = models.EmailField(unique=True, blank=False, null=False)  
    username = models.CharField(max_length=150, blank=True, null=True)
    profile = models.ImageField(upload_to='profile/', blank=True, null=True)
    cover_photo = models.ImageField(upload_to='cover_photo/', blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=False, null=False)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    bio = models.TextField(blank=True, null=True)
    nick_name = models.CharField(max_length=254,blank=True, null=True)
    fcm_token = models.CharField(max_length=254,blank=True, null=True)
    gender = models.CharField(max_length=54, choices=GENDER_CHOICES,blank=True, null=True)
    birth_day = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_svip = models.BooleanField(default=False)
    country = models.ForeignKey(Country, on_delete=models.CASCADE,null=True,blank=True)
    level = models.ForeignKey(UserLV, related_name='level', on_delete=models.CASCADE,null=True,blank=True)

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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] 

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email.split('@')[0]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} -> {self.user.username}"




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
