from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView
from django.http import JsonResponse

# class CustomLoginAdminView(TemplateView):
#     template_name = 'admin/login.html'
    


class UserListAdminView(TemplateView):
    login_url = '/login/'
    template_name = 'admin/user/user_list.html'



class UserEditView(TemplateView):
    template_name = 'admin/user/user_edit.html'
    login_url = '/login/'

    def get(self,request,*args, **kwargs):
        return super().get(self,request,*args, **kwargs)

    def get_context_data(self,*args, **kwargs):
        kwargs['id_user'] = self.request.GET['id_user']
        context = super().get_context_data(*args, **kwargs)
        return context   

# def UserListAdmin(request):
    # return render(request, 'admin/user/user_list.html')


def Register(request):
    return render(request, 'base/register.html')


def ForgetPassword(request):
    return render(request, 'base/forget.html')


def AccountSetting(request):
    return render(request, 'admin/account_setting.html')


def AdminPage(request):
    return render(request, 'admin/admin_page.html')


def Reports(request):
    return render(request, 'admin/user/user_list.html')


def Payments(request):
    return render(request, 'admin/payments.html')


def ReferralSystem(request):
    return render(request, 'admin/referral_code.html')


def DomainApps(request):
    return render(request, 'admin/domain_apps.html')


def HelpCenter(request):
    return render(request, 'admin/help_center.html')

