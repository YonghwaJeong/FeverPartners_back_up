from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth import login,logout
from .models import User
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage

def start(request):
    return render(request, "user_management/start.html")

# 로그인
def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            print('Is valid')
            email = form.cleaned_data.get("email")
            raw_password = form.cleaned_data.get("password")
            user = User.objects.get(email=email)
            
            if user.check_password(raw_password):
                print('Is valid2')
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect("user_management:main")
    # GET
    else:
        form = LoginForm()
    return render(request, "user_management/login.html", {"form": form})

# 소셜 회원가입 시 회원정보 입력
def user_update_start(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            return redirect('user_management:main')  # nickname 설정 후 메인 페이지로 이동
    else:
        # 이미 회원가입을 해서 nickname이 있다면 main으로 이동
        if request.user.new == True:
            form = UserUpdateForm(instance=None)
            if request.user.email == "" or request.user.email == None:
                request.user.email = request.user.id
                request.user.new = False
                request.user.save()
            return render(request, 'user_management/input_nickname.html', {'form': form})
        return redirect("user_management:main")

# 로그아웃
def user_logout(request):
    logout(request)
    return redirect("user_management:start")

# 회원가입 유형 선택 페이지
def user_signup(request):
    return render(request, "user_management/signup.html")

# 이메일로 회원가입
def user_signup_email(request):
    if request.method == "GET":
        form = CustomUserCreationForm()
        ctx = {
            "form": form,
        }
        return render(request, "user_management/signup_email.html", ctx)
    form = CustomUserCreationForm(request.POST)
    error_data = form.errors.as_data()
    if form.is_valid():
        user = form.save()
        user.new = False
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend') # 회원가입한 사용자를 자동으로 로그인
        return redirect("user_management:update") # 회원가입 성공 시 리다이렉트
    else:
        print(error_data)
        return redirect("user_management:signup_email")

# 유저 정보 업데이트
def user_update(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('user_management:main')  # nickname 설정 후 메인 페이지로 이동
    else:
        form = UserUpdateForm(instance=None)

    return render(request, 'user_management/input_nickname.html', {'form': form})

# 메인 화면
def main(request):
    user = request.user
    goals = user.goal.all()
    goal_count = goals.count()
    goal_complete = goals.filter(is_completed=True).count()
    ctx = {
        "goal_count": goal_count,
        "goal_complete": goal_complete,
    }
    return render(request, "user_management/main.html", ctx)

#유저 정보(user detail)
@login_required
def detail(request, pk):
    return render(request, 'user_management/user_detail.html')

def update(request, pk):
    user = User.objects.get(id=pk)
    if request.method == "POST":
        user.nickname = request.POST["nickname"]
        user.profile = request.POST["profile"]
        user.region = request.POST["region"]
        user.region_detail = request.POST["region_detail"]
        if 'profile_image' in request.FILES:
            profile_image = request.FILES['profile_image']
            if user.profile_image:
                default_storage.delete(user.profile_image.name)
            profile_image.name = f"{user.id}_{profile_image.name}"
            user.profile_image.save(profile_image.name, profile_image)
        user.save()
        return redirect(f"/detail/{pk}")
    form = UserUpdateForm(instance=user)
    cnt = {
        'form':form,
    }
    return render(request, 'user_management/user_update.html', cnt)
