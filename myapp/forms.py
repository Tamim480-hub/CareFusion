from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class SignUpForm(UserCreationForm):
    role = forms.ChoiceField(choices=[('doctor', 'Doctor'), ('patient', 'Patient')])
    phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role', 'phone')


class SignInForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)