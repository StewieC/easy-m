# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")
    display_name = forms.CharField(max_length=100, required=True, help_text="Required. This will be visible to others.")
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, help_text="Your password must be at least 8 characters long.")
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput, help_text="Enter the same password as above.")

    class Meta:
        model = User
        fields = ('email', 'username', 'display_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)