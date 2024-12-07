from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, SetPasswordForm
from django import forms
from hapi_app.models import User
from core.settings import MAXIMUM_PASSWORD_LENGTH, MINIMUM_PASSWORD_LENGTH

class UserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = User
        fields = '__all__'


class UserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = '__all__'


class UserAuthForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(
                _("This account is inactive."),
                code = 'inactive',
            ) 