from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.cache import cache

MAX_LOGIN_ATTEMPTS = 5
LOGIN_ATTEMPT_WINDOW = 60 * 15  # 15 minutes


def _login_attempts_key(username):
    return f'login_attempts:{username.strip().lower()}'


def employee_login(request):
    if request.user.is_authenticated:
        return redirect('projects_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        key = _login_attempts_key(username)
        attempts = cache.get(key, 0)

        if attempts >= MAX_LOGIN_ATTEMPTS:
            messages.error(request, 'تم إيقاف الدخول مؤقتاً بسبب محاولات فاشلة متكررة، يرجى المحاولة مرة أخرى بعد 15 دقيقة')
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                cache.delete(key)
                login(request, user)
                return redirect('projects_dashboard')
            else:
                cache.set(key, attempts + 1, LOGIN_ATTEMPT_WINDOW)
                messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')

    return render(request, 'system/login.html')


def employee_logout(request):
    logout(request)
    return redirect('employee_login')


def system_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('employee_login')
    return render(request, 'system/dashboard.html')
