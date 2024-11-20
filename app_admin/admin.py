from django.contrib import admin
from .models import Advertiser, Publisher, Ad, Impression

admin.site.register(Advertiser)
admin.site.register(Publisher)
admin.site.register(Ad)
admin.site.register(Impression)

