from django.contrib import admin
from .models import User,Follower,UserProfileVisit,Invitation,Wallet,Image,WalletLog

admin.site.register(User)
admin.site.register(Follower)
admin.site.register(UserProfileVisit)
admin.site.register(Invitation)
admin.site.register(Wallet)
admin.site.register(Image)
admin.site.register(WalletLog)
