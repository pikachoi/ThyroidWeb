from django import forms
from django.core.exceptions import ValidationError
from .models import Doctor, Doctor_profile, DoctorManager

class LoginForm(forms.Form):
    username = forms.CharField(
        # min_length=3,  # 정의 시 기본 에러 메시지가 우선출력
        widget=forms.HiddenInput(),  # 숨김
    )  
    password = forms.CharField(
        widget=forms.HiddenInput(), 
    )

    # clean_ 접두사 사용 시 자동호출
    def clean_username(self):
        username = self.cleaned_data["username"]  # 데이터 검증
        if len(username) < 5 or len(username) > 25:
            raise ValidationError("아이디는 최소 5자리에서 최대 25자리 사이여야 합니다.")
        return username
        
    def clean_password(self):
        password = self.cleaned_data.get("password")
        if len(password) < 8 or len(password) > 25:
            raise ValidationError("비밀번호는 최소 8자리에서 최대 25자리 사이여야 합니다.")
        return password
    

        # if Doctor.objects.filter(username=username).exists():
        #     raise ValidationError(f"입력한 사용자명({username})은 이미 사용 중입니다.")