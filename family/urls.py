from django.urls import path
from .views import MyFamilyMembersAPIView,GetPendingFamilyMembersAPIView,FamilyBonusLevelDetailAPIView,FamilyMembersAPIView,UserLVAPPListView,CreateFamilyAPIView,LastWeekFamilyRankingAPIView,WeeklyFamilyRankingAPIView,WeeklyBonusDistributionAPIView, FamilyMemberAPIView,WeeklyFamilyAndMemberContributionAPIView,DeleteInactiveFamiliesAPIView,ManageFamilyMemberAPIView,LeaveFamilyAPIView
from family.fake_views import GenerateFakeDataView,CreateFakeBonusLevelAPIView

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
    path('app-level-details/', UserLVAPPListView.as_view(), name='app_level_details'),
    path('generate-fake-data/', GenerateFakeDataView.as_view(), name='generate_fake_data'),
    path('family/members/<int:family_id>/', FamilyMembersAPIView.as_view(), name='family-members'),
    path('family-bonus-level/<int:family_id>/', FamilyBonusLevelDetailAPIView.as_view(), name='family-bonus-level-detail'),
    path('create-fake-bonus-levels/', CreateFakeBonusLevelAPIView.as_view(), name='create-fake-bonus-levels'),
    path('family-member-join-request/', GetPendingFamilyMembersAPIView.as_view(), name='family-member-join-request'),
    path('my-family-members/<int:created_by_id>/', MyFamilyMembersAPIView.as_view(), name='my-family-members'),
]
