from django.urls import path
from .views import CPLevelCreateAPIView,LevelUpGiftAPIView,CancelAllRelationshipsAPIView,CreateRelationshipInviteView,AcceptOrDeclineRelationshipView,CheckAndCancelExpiredRelationships

urlpatterns = [
    path('create-cp-level/', CPLevelCreateAPIView.as_view(), name='create-cp-level'),
    path('relationship/invite/<int:user1_id>/', CreateRelationshipInviteView.as_view(), name='create_relationship_invite'),
    path('relationship/accept/<int:relationship_id>/', AcceptOrDeclineRelationshipView.as_view(), name='accept_or_decline_relationship'),
    path('relationships/check_expiration/', CheckAndCancelExpiredRelationships.as_view(), name='check-expired-relationships'),
    path('level-up-cp/<int:user_id>/', LevelUpGiftAPIView.as_view(), name='level-up-cp'),
    path("cancel-all-relationships/", CancelAllRelationshipsAPIView.as_view(), name="cancel-all-relationships"),
    
]
