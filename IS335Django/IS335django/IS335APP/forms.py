from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User  # You can also use a custom user model if needed

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    phone_number = forms.CharField(max_length=10, min_length=10, required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if len(phone_number) != 10:
            raise ValidationError("Phone number must be 10 digits")
        if User.objects.filter(username=phone_number).exists():  # Fix filter by username if you're using phone_number uniquely
            raise ValidationError("Phone number already exists")
        return phone_number

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError("Password must be more than 8 characters")
        return password

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists")
        return username
