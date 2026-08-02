import json
from datetime import timedelta

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.cache import cache
from django.db.models import F
from django.shortcuts import render, redirect
from django.utils import timezone

MAX_LOGIN_ATTEMPTS = 5
LOGIN_ATTEMPT_WINDOW = 60 * 15  # 15 minutes

LOGIN_URL = '/dashboard/login/'


def _login_attempts_key(username):
    return f'login_attempts:{username.strip().lower()}'


def employee_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard_home')

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
                return redirect('dashboard_home')
            else:
                cache.set(key, attempts + 1, LOGIN_ATTEMPT_WINDOW)
                messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')

    return render(request, 'dashboard/login.html')


def employee_logout(request):
    logout(request)
    return redirect('employee_login')


@login_required(login_url=LOGIN_URL)
def dashboard_home(request):
    from invoices.models import Invoice
    from inventory.models import Item
    from projects.models import Project, Task
    from clients.models import Client

    today = timezone.now().date()

    # ── Stat cards ──────────────────────────────────────────────
    projects = Project.objects.all()
    active = projects.filter(status='active').count()
    planning = projects.filter(status='planning').count()
    tasks_today = Task.objects.filter(
        assigned_to=request.user,
        due_date=today,
        status__in=['todo', 'in_progress'],
    ).count()
    overdue_invoices_count = Invoice.objects.filter(
        due_date__lte=today
    ).exclude(status='fully_paid').count()

    # ── Calendar events JSON ─────────────────────────────────────
    cal_events = []
    user_tasks = Task.objects.filter(
        assigned_to=request.user
    ).exclude(status='done').filter(due_date__isnull=False)
    for t in user_tasks:
        cal_events.append({
            'date': t.due_date.strftime('%Y-%m-%d'),
            'type': 'task',
            'label': t.title,
            'url': f'/projects/tasks/{t.pk}/',
        })
    inv_qs = Invoice.objects.exclude(status='fully_paid').filter(due_date__isnull=False)
    for inv in inv_qs:
        cal_events.append({
            'date': inv.due_date.strftime('%Y-%m-%d'),
            'type': 'invoice',
            'label': f'فاتورة {inv.invoice_number}',
            'url': f'/invoices/{inv.pk}/',
        })
    proj_qs = Project.objects.filter(end_date__isnull=False)
    for p in proj_qs:
        cal_events.append({
            'date': p.end_date.strftime('%Y-%m-%d'),
            'type': 'project',
            'label': p.name,
            'url': f'/projects/{p.pk}/',
        })

    # ── Active/Planning projects ─────────────────────────────────
    active_projects = Project.objects.filter(
        status__in=['active', 'planning']
    ).select_related()[:6]

    # ── Notifications ────────────────────────────────────────────
    notifications = []

    low_stock = Item.objects.filter(qty_on_hand__lte=F('reorder_level'))
    for item in low_stock[:5]:
        notifications.append({
            'type': 'danger',
            'icon': 'box',
            'text': f'مخزون منخفض: {item.name} ({item.qty_on_hand} متبقي)',
        })

    overdue_inv = Invoice.objects.filter(
        due_date__lt=today
    ).exclude(status='fully_paid').select_related('client')[:5]
    for inv in overdue_inv:
        days = (today - inv.due_date).days
        client_name = inv.client.name if inv.client else '—'
        notifications.append({
            'type': 'danger',
            'icon': 'invoice',
            'text': f'فاتورة متأخرة: {inv.invoice_number} — {client_name} (منذ {days} أيام)',
        })

    soon = today + timedelta(days=14)
    ending_soon = Project.objects.filter(
        end_date__gte=today, end_date__lte=soon,
        status__in=['active', 'planning']
    )
    for p in ending_soon[:5]:
        days_left = (p.end_date - today).days
        notifications.append({
            'type': 'warning',
            'icon': 'project',
            'text': f'مشروع يقترب من نهايته: {p.name} (بعد {days_left} أيام)',
        })

    overdue_tasks = Task.objects.filter(
        assigned_to=request.user,
        due_date__lt=today,
        status__in=['todo', 'in_progress'],
    ).select_related('project')[:5]
    for t in overdue_tasks:
        days = (today - t.due_date).days
        notifications.append({
            'type': 'warning',
            'icon': 'task',
            'text': f'مهمة متأخرة: {t.title} (منذ {days} أيام)',
        })

    # ── Quick-add data ───────────────────────────────────────────
    ctx = {
        'active_tab': 'dashboard',
        'today': today,
        'active': active,
        'planning': planning,
        'tasks_today': tasks_today,
        'overdue_invoices_count': overdue_invoices_count,
        'cal_events_json': json.dumps(cal_events),
        'active_projects': active_projects,
        'notifications': notifications,
        'all_users': User.objects.filter(is_active=True),
        'all_projects': Project.objects.all(),
        'all_clients': Client.objects.all(),
    }
    return render(request, 'dashboard/index.html', ctx)
