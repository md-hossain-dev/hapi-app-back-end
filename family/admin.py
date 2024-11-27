from django.contrib import admin
from .models import CreateFamily,FamilyMember,TransactionLog,WeeklyRanking,BonusLevel

admin.site.register(CreateFamily)
admin.site.register(FamilyMember)
admin.site.register(TransactionLog)
admin.site.register(WeeklyRanking)
admin.site.register(BonusLevel)
