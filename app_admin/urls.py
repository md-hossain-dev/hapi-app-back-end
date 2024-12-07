from django.contrib import admin
from django.urls import path,include

from django.conf.urls.static import static
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.generic import TemplateView

from django.urls import path
from . import views

from app_admin.admin_views import LoginPageView,LogoutView,UserLVListView,CountryListView,AllUserViewList,UserUpdateAPIView,UserDetailView,UserDeleteView
from app_admin.security_views import TokenObtainPairView, TokenRefreshView,UserIdView

from app_admin.views import UserListAdminView,UserEditView


urlpatterns = [

    path('user-lists/', AllUserViewList.as_view(), name='user_lists'),
    path('user-update/<int:pk>/', UserUpdateAPIView.as_view(), name='user-update'),
    path('delete-user/<int:user_id>/', UserDeleteView.as_view(), name='delete-user'),
    path('user-details/<int:pk>/', UserDetailView.as_view(), name='delete_details'),

    path('country-details/', CountryListView.as_view(), name='country_details'),
    path('level-details/', UserLVListView.as_view(), name='level_details'),
    
    path('login/', LoginPageView.as_view(), name='login_users'), 
    path('logout/', LogoutView.as_view(), name='logout'), 
    path('token/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user-id/', UserIdView.as_view(), name='user_id'),


    

    path('user-list/', UserListAdminView.as_view(), name='user_list'), 
    path('user-edit/', UserEditView.as_view(), name='user_edit'), 

    # path('user-list/', views.UserListAdmin, name='user_list'),

    path('register/', views.Register, name='register'),
    path('forget/', views.ForgetPassword, name='forget'),
    path('account-setting/', views.AccountSetting, name='account_setting'),
    path('dashboard/', views.AdminPage, name='dashboard'),
    
    path('payments/', views.Payments, name='payments'),
    path('referral-system/', views.ReferralSystem, name='referral_system'),
    path('domain-apps/', views.DomainApps, name='domain_apps'),
    path('help-center/', views.HelpCenter, name='help_center'),

]

