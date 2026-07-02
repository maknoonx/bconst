from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def employee_login(request):
    if request.user.is_authenticated:
        return redirect('projects_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('projects_dashboard')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')

    return render(request, 'system/login.html')


def employee_logout(request):
    logout(request)
    return redirect('employee_login')


def system_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('employee_login')
    return render(request, 'system/dashboard.html')
