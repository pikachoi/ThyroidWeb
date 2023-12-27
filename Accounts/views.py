import re

from django.contrib import auth
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate

from .models import Doctor, Doctor_profile, Question


def login(request) :
    if request.method == "POST" :
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username = username, password = password)

        if user is None :
            return render(request, "Accounts_login.html", context = {"check_info" : "아이디와 비밀번호를 확인해주세요!"})
        else :
            auth.login(request, user)
            return redirect("diagnosis_home") 
    else :
        return render(request, "Accounts_login.html")

def logout(request) :
    auth.logout(request)
    return redirect("login")


def signup(request) :
    question = [q.question for q in Question.objects.all()]
    if request.method == "POST" :
        license_number = request.POST["License_Number"]
    
        if Doctor_profile.objects.filter(license=license_number).exists():
            return render(request, "Accounts_signup.html", context={"question": question, "exists_license": "이미 등록된 의사면허번호입니다."})
        
        if Doctor.object.filter(username = request.POST["username"]).exists() :
            return render(request, "Accounts_signup.html", context = {"question" : question, "exists_id" : "존재하는 아이디입니다."})
        
        elif not re.search(r"^[\w*$]{5,25}", (request.POST['username'])):
            return render(request, "Accounts_signup.html", context = {"question" : question,"check_username" : "아이디는 5~25 글자의 영어 대 소문자, 숫자만 입력 가능합니다."})
        
        elif not re.search(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@!%*#?&])[A-Za-z\d@!%*#?&]{8,20}$",(request.POST['password1'])):
            return render(request, "Accounts_signup.html", context = {"question" : question,"check_password" : "비밀번호는 10~25 글자의 영어 대 소문자, 숫자, 특수문자를 사용하세요."})

        elif re.search(r'[^0-9]{11}',(request.POST['phonenumber'])):
            return render(request, "Accounts_signup.html", context = {"question" : question,"wrong_phone" : "휴대폰번호는 '-'없이 입력하세요."})

        elif request.POST["password1"] != request.POST["password2"] :
            return render(request, "Accounts_signup.html", context = {"question" : question, "wrong_password" : "비밀번호가 일치하지 않습니다!"})

        else :
            doctor = Doctor.object.create_user(
                username = request.POST["username"],
                password = request.POST["password1"],
            )
            auth.login(request, doctor)

            Doctor_profile.objects.create(
                doctor_username = Doctor.object.get(username = request.POST["username"]),
                license=license_number,
                real_name       = request.POST["name"],
                email           = request.POST["email"],
                phone           = request.POST["phonenumber"],
                belong          = request.POST["Affiliation"],
                position        = request.POST["Rank"],
                medical_subject = request.POST["Subject"],
                question        = Question.objects.get(question = request.POST["question"]),
                question_answer = request.POST["hint"],
            )
            return render(request, "Accounts_login.html", context = {"success_signup" : "회원가입이 완료되었습니다!"})
    return render(request, "Accounts_signup.html", context = {"question" : question} )


def id_search(request):
    question = [q.question for q in Question.objects.all()]
    
    if request.method == "POST":
        hint = request.POST.get("hint", "")
        question_text = request.POST.get("question", "")
        real_name = request.POST.get("name", "")
        email = request.POST.get("email", "")
        license_number = request.POST.get("License_Number", "")
        
        try:
            question_obj = Question.objects.get(question=question_text)
            doctor_profiles = Doctor_profile.objects.filter(question=question_obj, question_answer=hint)
            
            # 입력한 정보와 Doctor_profile의 정보를 비교하여 일치 여부를 확인
            matching_profiles = []
            for profile in doctor_profiles:
                if (profile.real_name == real_name) and (profile.email == email) and (profile.license == license_number):
                    matching_profiles.append(profile)
            
            if not matching_profiles:
                return render(request, "Accounts_id_search.html",
                              context={"question": question, "error": "일치하는 정보가 없습니다. 다시 입력해주세요."})
            
            if len(matching_profiles) == 1:
                return render(request, "Accounts_id_search.html",
                              context={"question": question,
                                       "real_name": f"{matching_profiles[0].real_name}님의 아이디는",
                                       "doctor_username": f"{matching_profiles[0].doctor_username.username}",
                                       "end_text": "입니다"})
            else:
                return render(request, "Accounts_id_search.html",
                              context={"question": question,
                                       "matching_profiles": matching_profiles})
        except Question.DoesNotExist:
            return render(request, "Accounts_id_search.html",
                          context={"question": question, "error": "일치하는 정보가 없습니다. 다시 입력해주세요."})
    
    return render(request, "Accounts_id_search.html", context={"question": question})



def password_search(request):
    question = [q.question for q in Question.objects.all()]
    
    if request.method == "POST":
        doctor_username = request.POST.get("pw_search_input", "")
        question_text = request.POST.get("question", "")
        real_name = request.POST.get("name", "")
        email = request.POST.get("email", "")
        license_number = request.POST.get("License_Number", "")
        hint = request.POST.get("hint", "")
        
        try:
            question_obj = Question.objects.get(question=question_text)
            doctor_profiles = Doctor_profile.objects.filter(
                question=question_obj, question_answer=hint
            )
            
            # 입력한 정보와 Doctor_profile의 정보를 비교하여 일치 여부를 확인
            matching_profiles = []
            for profile in doctor_profiles:
                if (profile.doctor_username.username == doctor_username) and (profile.real_name == real_name) and (profile.email == email) and (profile.license == license_number):
                    matching_profiles.append(profile)
            
            if not matching_profiles:
                return render(
                    request,
                    "Accounts_password_search.html",
                    context={"question": question, "error": "일치하는 정보가 없습니다. 다시 입력해주세요."},
                )
            elif len(matching_profiles) == 1:
                request.session["reset_username"] = matching_profiles[0].doctor_username.username
                return redirect("password_reset")
            else:
                return render(
                    request,
                    "Accounts_password_search.html",
                    context={"question": question, "matching_profiles": matching_profiles},
                )
        except Question.DoesNotExist:
            return render(
                request,
                "Accounts_password_search.html",
                context={"question": question, "error": "일치하는 정보가 없습니다. 다시 입력해주세요."},
            )
    
    return render(request, "Accounts_password_search.html", context={"question": question})


def password_reset(request):
    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        
        if password1 != password2:
            return render(request, "Accounts_password_reset.html", {"error": "비밀번호가 일치하지 않습니다."})
        
        # 비밀번호 재설정 로직
        username = request.session.get("reset_username")
        context = {"check_password" : "비밀번호는 10~25 글자의 영어 대 소문자, 숫자, 특수문자를 사용하세요."}
        if username:
            try:
                if not re.search(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@!%*#?&])[A-Za-z\d@!%*#?&]{8,20}$",(request.POST['password1'])):
                    return render(request, "Accounts_password_reset.html", context=context)
                doctor = Doctor.object.get(username=username)
                doctor.set_password(password1)
                doctor.save()
                request.session.pop("reset_username")  # 비밀번호 재설정 완료 후 세션에서 삭제
                return render(request, "Accounts_login.html", {"password_reset_success": "비밀번호가 재설정되었습니다."})
            except Doctor.DoesNotExist:
                return render(request, "Accounts_password_reset.html")
        
        return render(request, "Accounts_password_reset.html", context=context)
    
    return render(request, "Accounts_password_reset.html")