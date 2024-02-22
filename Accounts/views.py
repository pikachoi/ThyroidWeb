import re
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import Doctor, Doctor_profile, Question
from .forms import LoginForm, SignUpForm
from django.views.decorators.cache import never_cache
from django.contrib import messages

@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return render(request, "Accounts_login_status.html")
    
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect("diagnosis_home")
            else:
                form.add_error(None, "등록되지 않은 아이디이거나 아이디 또는 비밀번호를 잘못 입력했습니다.")
    else:
        form = LoginForm()

    context = {"form": form}
    return render(request, "Accounts_login.html", context)


def logout_view(request) :
    logout(request)
    return redirect("login")


@never_cache
def signup_view(request):
    if request.user.is_authenticated:
        return render(request, "Accounts_login_status.html")
        
    question = [q.question for q in Question.objects.all()]

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        
        if form.is_valid():
            user = Doctor.object.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                
            )

            Doctor_profile.objects.create(
                doctor_username=user,
                license=form.cleaned_data['License_Number'],
                real_name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phonenumber'],
                belong=form.cleaned_data['Affiliation'],
                position=form.cleaned_data['Rank'],
                medical_subject=form.cleaned_data['Subject'],
                question=Question.objects.get(question = request.POST["question"]),
                question_answer=form.cleaned_data['hint'],
            )
            messages.success(request, "회원가입이 완료되었습니다! 로그인 해주세요.")
            return redirect("login")
    else:
        form = SignUpForm()

    return render(request, "Accounts_signup.html", {"form": form, "question": question})


@never_cache
def id_search(request):
    if request.user.is_authenticated:
        return render(request, "Accounts_login_status.html")
    
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


@never_cache
def password_search(request):
    if request.user.is_authenticated:
        return render(request, "Accounts_login_status.html")
    
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


@never_cache
def password_reset(request):
    if request.user.is_authenticated:
        return render(request, "Accounts_login_status.html")
    
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