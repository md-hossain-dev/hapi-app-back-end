from django.urls import path
from .views import CreateFamilyAPIView,LastWeekFamilyRankingAPIView,WeeklyFamilyRankingAPIView,WeeklyBonusDistributionAPIView, FamilyMemberAPIView,WeeklyFamilyAndMemberContributionAPIView,DeleteInactiveFamiliesAPIView,ManageFamilyMemberAPIView,LeaveFamilyAPIView

urlpatterns = [
    path('create-family/', CreateFamilyAPIView.as_view(), name='create-family'),
    path('family-members/', FamilyMemberAPIView.as_view(), name='family-members'),
    path('manage-family-member/', ManageFamilyMemberAPIView.as_view(), name='manage-family-member'),
    path('leave-family/', LeaveFamilyAPIView.as_view(), name='leave-family'),
    path('delete-inactive-families/', DeleteInactiveFamiliesAPIView.as_view(), name='delete_inactive_families'),
    path('update-weekly-family-member-contributions/', WeeklyFamilyAndMemberContributionAPIView.as_view(), name='update-weekly-family-member-contributions'),
    path('weekly-bonus/', WeeklyBonusDistributionAPIView.as_view(), name='weekly-bonus'),
    path('weekly-family-ranking/', WeeklyFamilyRankingAPIView.as_view(), name='weekly-family-ranking'),
    path('last-week-family-ranking/', LastWeekFamilyRankingAPIView.as_view(), name='last-week-family-ranking'),
]
