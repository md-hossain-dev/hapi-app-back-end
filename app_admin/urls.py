from django.contrib import admin
from django.urls import path,include

from django.conf.urls.static import static
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.generic import TemplateView

from django.urls import path
from . import views

from app_admin.admin_views import CategoryDetailView,ProductCategoryDeleteAPIView,CategoryUpdateAPIView,ProductRetrieveAPIView,CategorytListStoreView,ProductDeleteAPIView,StoreUpdateAPIView,LoginPageView,LogoutView,UserLVListView,AllStoreCategoryViewList,AllStoreViewList,CountryListView,AllUserViewList,UserUpdateAPIView,StoreDetailView,UserDetailView,UserDeleteView
from app_admin.security_views import TokenObtainPairView, TokenRefreshView,UserIdView

from app_admin.views import CatagoryEditView,UserListAdminView,StoreEditView,UserEditView,StoreListAdminView,CatagoryStoreListAdminView


urlpatterns = [

    path('user-lists/', AllUserViewList.as_view(), name='user_lists'),
    path('user-update/<int:pk>/', UserUpdateAPIView.as_view(), name='user-update'),
    path('delete-user/<int:user_id>/', UserDeleteView.as_view(), name='delete-user'),
    path('user-details/<int:pk>/', UserDetailView.as_view(), name='delete_details'),
    

    path('store-lists/', AllStoreViewList.as_view(), name='store_lists'),
    path('category-lists-store/', AllStoreCategoryViewList.as_view(), name='category_lists_store'),

    

    path('country-details/', CountryListView.as_view(), name='country_details'),
    path('level-details/', UserLVListView.as_view(), name='level_details'),
    # path('store-details/', ProductListStoreView.as_view(), name='store_details'),
    path('category-details/', CategorytListStoreView.as_view(), name='category_details'),

    
    path('login/', LoginPageView.as_view(), name='login_users'), 
    path('logout/', LogoutView.as_view(), name='logout'), 
    path('token/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user-id/', UserIdView.as_view(), name='user_id'),


    

    path('user-list/', UserListAdminView.as_view(), name='user_list'), 
    path('user-edit/', UserEditView.as_view(), name='user_edit'),

    path('store-edit/', StoreEditView.as_view(), name='store_edit'),
    path('catagory-edit/', CatagoryEditView.as_view(), name='catagory_edit'),


    path('store-list/', StoreListAdminView.as_view(), name='store_list'),
    path('product/<int:pk>/', ProductRetrieveAPIView.as_view(), name='product-retrieve'),
    path('store/delete/<int:pk>/', ProductDeleteAPIView.as_view(), name='product-delete'),
    path('store-update/<int:pk>/', StoreUpdateAPIView.as_view(), name='store-update'),
    path('store-info/<int:pk>/', StoreDetailView.as_view(), name='store_info'),
    path('catagory-list/', CatagoryStoreListAdminView.as_view(), name='catagory_list'), 
    path('catagory-update/<int:pk>/', CategoryUpdateAPIView.as_view(), name='catagory_update'), 
    path('catagory-info/<int:pk>/', CategoryDetailView.as_view(), name='catagory_info'),
    
    path('catagory/delete/<int:pk>/', ProductCategoryDeleteAPIView.as_view(), name='catagory-delete'),

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

