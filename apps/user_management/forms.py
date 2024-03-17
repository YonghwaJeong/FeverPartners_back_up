from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        help_text='Enter your email',
        widget=forms.EmailInput(attrs={'placeholder': '이메일 입력'}))
    
    password1 = forms.CharField(
        max_length=30, required=True, widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "비밀번호 입력"})
    )

    password2 = forms.CharField(
        max_length=30, required=True, widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "비밀번호 확인"})
    )

    class Meta:
        model = User
        fields = ["email", "password1", "password2"]


class UserUpdateForm(UserChangeForm):
    nickname = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '닉네임 입력'}))
    profile = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '소개글 입력'}))
    region = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '거주지역 입력'}))
    region_detail = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '거주지역 세부 입력'}))

    class Meta:
        model = User
        fields = ["nickname", "profile", "profile_image", "region", "region_detail"]


class LoginForm(forms.Form):
    email = forms.CharField(
        max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "이메일 입력"})
    )
    password = forms.CharField(
        max_length=30, required=True, widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "비밀번호 입력"})
    )