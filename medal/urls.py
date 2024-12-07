from django.urls import path
from .views import MedalInfoCreateAPIView,SingleUserMedalsAPIView,MedalInfoByTypeAPIView,UpdateOrCreateUserMedalAPIView,UpdateUserMedalsAPIView

urlpatterns = [
    path('create-medal/', MedalInfoCreateAPIView.as_view(), name='create-medal'),
    path('medals-by-type/', MedalInfoByTypeAPIView.as_view(), name='medals-by-type'),
    path('update-or-create-user-medal/', UpdateOrCreateUserMedalAPIView.as_view(), name='update-or-create-user-medal'),
    path('update-user-medals/', UpdateUserMedalsAPIView.as_view(), name='update_user_medals'),
    path('single-user-medals/', SingleUserMedalsAPIView.as_view(), name='single_user_medals'),
]
