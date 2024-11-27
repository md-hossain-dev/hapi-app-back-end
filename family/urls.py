from django.urls import path
from .views import CreateFamilyAPIView, FamilyMemberAPIView,FamilyContributionAPI,DeleteInactiveFamiliesAPIView,ManageFamilyMemberAPIView,LeaveFamilyAPIView

urlpatterns = [
    path('create-family/', CreateFamilyAPIView.as_view(), name='create-family'),
    path('family-members/', FamilyMemberAPIView.as_view(), name='family-members'),
    path('manage-family-member/', ManageFamilyMemberAPIView.as_view(), name='manage-family-member'),
    path('leave-family/', LeaveFamilyAPIView.as_view(), name='leave-family'),
    path('delete-inactive-families/', DeleteInactiveFamiliesAPIView.as_view(), name='delete_inactive_families'),
    path('family-contribution/', FamilyContributionAPI.as_view(), name='family-contribution'),
]
