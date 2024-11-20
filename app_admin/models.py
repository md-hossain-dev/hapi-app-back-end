from django.db import models
from hapi_app.models import User

class Advertiser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.company_name

class Publisher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    website_url = models.URLField()

    def __str__(self):
        return self.user.username

class Ad(models.Model):
    advertiser = models.ForeignKey(Advertiser, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='ads/')
    url = models.URLField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Impression(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ad.title} - {self.timestamp}"
