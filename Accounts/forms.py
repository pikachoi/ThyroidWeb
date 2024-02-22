from typing import Any
from django import forms
from django.core.exceptions import ValidationError
from .models import Doctor, Doctor_profile, DoctorManager, Question
import re
from django.views.decorators.cache import never_cache


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.HiddenInput())  
    password = forms.CharField(widget=forms.HiddenInput())

    def clean_username(self):
        username = self.cleaned_data["username"]  
        if len(username) < 5 or len(username) > 25:
            raise ValidationError("아이디는 최소 5자리에서 최대 25자리 사이여야 합니다.")
        return username
        
    def clean_password(self):
        password = self.cleaned_data["password"]
        if len(password) < 8 or len(password) > 25:
            raise ValidationError("비밀번호는 최소 8자리에서 최대 25자리 사이여야 합니다.")
        return password
    

class SignUpForm(forms.Form):
    username       = forms.CharField(widget=forms.HiddenInput())
    password1      = forms.CharField(widget=forms.HiddenInput())
    password2      = forms.CharField(widget=forms.HiddenInput())
    name           = forms.CharField(widget=forms.HiddenInput())
    email          = forms.CharField(widget=forms.HiddenInput())
    phonenumber    = forms.CharField(widget=forms.HiddenInput())
    Affiliation    = forms.CharField(widget=forms.HiddenInput())
    Rank           = forms.CharField(widget=forms.HiddenInput())
    Subject        = forms.CharField(widget=forms.HiddenInput())
    question       = forms.CharField(widget=forms.HiddenInput())
    hint           = forms.CharField(widget=forms.HiddenInput())
    License_Number = forms.CharField(widget=forms.HiddenInput())
    
    def clean_username(self):
        username = self.cleaned_data['username']
        print(username)
        if Doctor.object.filter(username=username).exists():
            raise ValidationError("이미 등록된 아이디 입니다.")
        if not re.match(r"^[a-zA-Z0-9]{5,25}$", username):
            raise ValidationError("아이디는 5~25 글자의 영어, 숫자만 입력 가능합니다.")
        return username

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@!%*#?&])[A-Za-z\d@!%*#?&]{8,20}$", password1):
            raise ValidationError("비밀번호는 8~20 이내로 영어, 숫자, 특수문자가 모두 포함되어야 합니다.")
        return password1

    def clean_password2(self):
        password2 = self.cleaned_data['password2']
        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@!%*#?&])[A-Za-z\d@!%*#?&]{8,20}$", password2):
            raise ValidationError("재확인 비밀번호는 8~20 이내로 영어, 숫자, 특수문자가 모두 포함되어야 합니다.")
        return password2
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if not re.match(r"^[0-9a-zA-Z]([-_\.]?[0-9a-zA-Z])*@[0-9a-zA-Z]([-_\.]?[0-9a-zA-Z])*\.[a-zA-Z]{2,3}$", email):
             raise ValidationError("유효하지 않은 이메일 형식입니다.")
        return email

    def clean_phonenumber(self):
        phonenumber = self.cleaned_data['phonenumber']
        if not re.match(r"^01[016789][0-9]{7,8}$", phonenumber):
            raise ValidationError("휴대폰번호는 '-' 없이 10~11자리 숫자만 입력하세요.")
        return phonenumber
    
    def clean_License_Number(self):
        License_Number = self.cleaned_data['License_Number']
        if Doctor_profile.objects.filter(license=License_Number).exists():
            raise ValidationError("이미 등록된 면허번호 입니다.")
        return License_Number

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error(password2, "재확인 비밀번호가 일치하지 않습니다.")
            
        return cleaned_data