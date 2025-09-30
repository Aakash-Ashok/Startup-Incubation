from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import CustomUser
from .models import MentorProfile


class MentorSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

class MentorProfileForm(forms.ModelForm):
    class Meta:
        model = MentorProfile
        fields = ('full_name', 'expertise', 'profile_pic')