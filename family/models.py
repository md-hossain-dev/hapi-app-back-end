from django.db import models
from hapi_app.models import User, UserLV
from django.core.exceptions import ValidationError


class BonusLevel(models.Model):
    level = models.PositiveIntegerField(unique=True) 
    target_contribution = models.BigIntegerField()
    leader_coins = models.BigIntegerField()
    top1_coins = models.BigIntegerField()
    top2_coins = models.BigIntegerField()
    top3_coins = models.BigIntegerField()

    def __str__(self):
        return f"Level {self.level}"

class CreateFamily(models.Model):
    MODE_CHOICES = (
        ("leader/co-leader review", "Leader/Co-Leader Review"), 
        ("join_freely", "Join Freely"),   
    ) 

    name = models.CharField(max_length=255, unique=True)
    family_notification = models.CharField(max_length=254, null=True, blank=True)
    join_mode = models.CharField(max_length=54, choices=MODE_CHOICES, default="leader/co-leader review") 
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_families")
    contribution = models.BigIntegerField(default=0)  
    bonus_level = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    level = models.ForeignKey(UserLV, related_name='level_family', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

    def clean(self):
        if self.contribution < 0:
            raise ValidationError("Contribution cannot be negative.")


    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class FamilyMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # User can only join one family
    family = models.ForeignKey(CreateFamily, on_delete=models.CASCADE, related_name="members")
    coins_contributed = models.PositiveIntegerField(default=0)  # Coins contributed by this member
    joined_at = models.DateTimeField(auto_now_add=True)
    is_join = models.BooleanField(default=False)
    contribution = models.BigIntegerField(default=0)
    is_leader = models.BooleanField(default=False)
    reward = models.BigIntegerField(default=0)


    @property
    def is_top_contributor(self):
        # Check if this member is the top contributor in their family
        top_member = self.family.members.order_by('-coins_contributed').first()
        return top_member == self

    def __str__(self):
        return f"{self.user.username} in {self.family.name}"

    def clean(self):
        if self.contribution < 0:
            raise ValidationError("Contribution cannot be negative.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class TransactionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    family = models.ForeignKey(CreateFamily, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)  # e.g., "create", "join", "contribute", "gift"
    coins_transferred = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} by {self.user} - {self.coins_transferred} coins"


class WeeklyRanking(models.Model):
    family = models.OneToOneField(CreateFamily, on_delete=models.CASCADE)
    ranking_date = models.DateField()

    @property
    def total_coins(self):
        return self.family.members.aggregate(models.Sum('coins_contributed'))['coins_contributed__sum'] or 0

    def __str__(self):
        return f"{self.family.name} - {self.total_coins} coins"
