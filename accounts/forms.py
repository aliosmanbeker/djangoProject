from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import MyUser

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=255, help_text="Required. Add a valid email address.")

    class Meta:
        model = MyUser
        fields = ('email', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email', max_length=255)
