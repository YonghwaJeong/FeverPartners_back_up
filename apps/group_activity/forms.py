from django import forms
from .models import Authentication, MemberAuthentication
import datetime

class AuthenticationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['start'].initial = datetime.datetime.now()
        self.fields['end'].initial = datetime.datetime.now() + datetime.timedelta(hours=2)

    class Meta:
        model = Authentication
        fields = ['start', 'end']
        labels = {
            'start': '인증시작',
            'end': '인증종료',
        }
        widgets = {
            'start': forms.TextInput(attrs={'class': 'flatpickr'}),
            'end': forms.TextInput(attrs={'class': 'flatpickr'}),
        }

class MemberAuthenticationForm(forms.ModelForm):
    class Meta:
        model = MemberAuthentication
        fields = ['content', 'image']
        labels = {
            'content': '내용',
            'image': '사진',
        }
        widgets = {
            'content': forms.Textarea(attrs={'class': 'auth-input'}),
            'image': forms.ClearableFileInput(attrs={'class': 'auth-input'}),
        }
