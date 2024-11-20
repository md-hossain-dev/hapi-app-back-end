from django.shortcuts import render, get_object_or_404
from .models import Ad, Impression
from django.contrib.auth.decorators import login_required


def Register(request):
    return render(request, 'base/register.html')


def ForgetPassword(request):
    return render(request, 'base/forget.html')


def AccountSetting(request):
    return render(request, 'admin/account_setting.html')


def AdminPage(request):
    return render(request, 'admin/admin_page.html')


def Reports(request):
    return render(request, 'admin/reports.html')


def Payments(request):
    return render(request, 'admin/payments.html')


def ReferralSystem(request):
    return render(request, 'admin/referral_code.html')


def DomainApps(request):
    return render(request, 'admin/domain_apps.html')


def HelpCenter(request):
    return render(request, 'admin/help_center.html')

