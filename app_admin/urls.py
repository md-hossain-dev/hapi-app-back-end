from django.contrib import admin
from django.urls import path,include

from django.conf.urls.static import static
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.generic import TemplateView

from django.urls import path
from . import views


urlpatterns = [

    path('register/', views.Register, name='register'),
    path('forget/', views.ForgetPassword, name='forget'),
    path('account-setting/', views.AccountSetting, name='account_setting'),
    path('dashboard/', views.AdminPage, name='dashboard'),
    path('reports/', views.Reports, name='reports'),
    path('payments/', views.Payments, name='payments'),
    path('referral-system/', views.ReferralSystem, name='referral_system'),
    path('domain-apps/', views.DomainApps, name='domain_apps'),
    path('help-center/', views.HelpCenter, name='help_center'),

]