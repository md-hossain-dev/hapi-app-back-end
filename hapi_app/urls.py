from django.urls import path
from .views import UserNotificationAPIView,UpdateFCMTokenAPIView,CustomObtainTokenView,GoogleAuthAPIView,UserWalletCountAPIView,UserProfileImageUpdateAPIView,CountryListAPIView,UserUpdateAPIView,CreateOrUpdateWalletAPIView,CustomRegisterUserView,UploadMultipleImagesAPIView,GetCoinsAPIView,InviteStatusAPIView,SingleInviteStatusAPIView,AcceptInviteAPIView,SendInviteAPIView,ProfileVisitCountAPIView,FollowUserAPIView,UserWithFollowersCountAPIView

urlpatterns = [
    path('login/', CustomObtainTokenView.as_view(), name='login'),
    path('login-with-google/', GoogleAuthAPIView.as_view(), name='login-with-google'),
    path('register/', CustomRegisterUserView.as_view(), name='custom_user_register'),
    path('follower/<int:user_id>/', FollowUserAPIView.as_view(), name='follow_user'),
    path('followers-count/<int:user_id>/', UserWithFollowersCountAPIView.as_view(), name='user_with_followers'),
    path('user/profile-visit/<int:user_id>/', ProfileVisitCountAPIView.as_view(), name='profile-visit'),
    path('send-invite/<int:inviter_id>/', SendInviteAPIView.as_view(), name='send-invite'),
    path('accept-invite/', AcceptInviteAPIView.as_view(), name='accept-invite'),
    path('single-invite-status/', SingleInviteStatusAPIView.as_view(), name='single-invite-status'),
    path('invite-status/', InviteStatusAPIView.as_view(), name='invite-status'),
    path('get-coins/', GetCoinsAPIView.as_view(), name='get-coins'),
    path('upload-images/<int:user_id>/', UploadMultipleImagesAPIView.as_view(), name='upload-multiple-images'),
    path('create-wallet/', CreateOrUpdateWalletAPIView.as_view(), name='create_wallet'),
    path('countries/', CountryListAPIView.as_view(), name='country-list'),
    path('user-update/', UserUpdateAPIView.as_view(), name='user-update'),
    path('update-profile-image/', UserProfileImageUpdateAPIView.as_view(), name='update-profile-image'),
    path('user-wallet/', UserWalletCountAPIView.as_view(), name='user_wallet'),
    path('update-fcm-token/', UpdateFCMTokenAPIView.as_view(), name='update-fcm-token'),
    path('user-notification/', UserNotificationAPIView.as_view(), name='user_notification'),
]