from django.contrib import admin
from .models import User,Follower,UserProfileVisit,Invitation,Wallet

admin.site.register(User)
admin.site.register(Follower)
admin.site.register(UserProfileVisit)
admin.site.register(Invitation)
admin.site.register(Wallet)
