from django.contrib import admin
from .models import User,Follower,UserProfileVisit,Invitation,Wallet,Image,WalletLog,UserLV,Country,Notification

admin.site.register(User)
admin.site.register(Follower)
admin.site.register(UserProfileVisit)
admin.site.register(Invitation)
admin.site.register(Wallet)
admin.site.register(Image)
admin.site.register(WalletLog)
admin.site.register(UserLV)
admin.site.register(Country)
admin.site.register(Notification)
