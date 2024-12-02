from django.contrib.auth.models import AbstractUser
from django.db import models
from hapi_app.models import User



class MedalInfo(models.Model):
    MEDAL_CHOICES = (
        ('Achievement', 'Achievement'),
        ('Gift', 'Gift'),
        ('Activity', 'Activity'),
    )
    medal_image = models.ImageField(upload_to='medal_image/', blank=True, null=True)
    medal_name = models.CharField(max_length=50, blank=False, null=False)
    medal_type = models.CharField(max_length=54, choices=MEDAL_CHOICES,blank=True, null=True)
    medal_star = models.PositiveIntegerField(default=0)
    medal_send_count = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.medal_name


class UserMedal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_medal')
    medal = models.ForeignKey(MedalInfo, on_delete=models.CASCADE, related_name='medal')
    send_count = models.PositiveIntegerField(default=0)
    is_show = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return self.medal

    def __str__(self):
        return f'{self.user.username} to {self.medal.medal_name}'




