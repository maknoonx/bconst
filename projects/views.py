import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Sum, F
from .models import Project, Task
from clients.models import Client


LOGIN_URL = '/system/'


def _parse_due_time(POST):
    hour = POST.get('due_time_hour', '').strip()
    minute = POST.get('due_time_min', '').strip()
    ampm = POST.get('due_time_ampm', '').strip()
    if not hour or not minute:
        return None
    try:
        h = int(hour)
        m = int(minute)
        if ampm == 'PM' and h != 12:
            h += 12
        elif ampm == 'AM' and h == 12:
            h = 0
        from datetime import time
        return time(h, m)
    except (ValueError, TypeError):
        return None


@login_required(login_url=LOGIN_URL)
def dashboard(request):
    from datetime import date, timedelta
    from invoices.models import Invoice
    from inventory.models import Item

    today = timezone.now().date()

    # ── Stat cards ──────────────────────────────────────────────
    projects  = Project.objects.all()
    active    = projects.filter(status='active').count()
    planning  = projects.filter(status='planning').count()
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

    # Low stock
    low_stock = Item.objects.filter(qty_on_hand__lte=F('reorder_level'))
    for item in low_stock[:5]:
        notifications.append({
            'type': 'danger',
            'icon': 'box',
            'text': f'مخزون منخفض: {item.name} ({item.qty_on_hand} متبقي)',
        })

    # Overdue invoices
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

    # Projects ending soon (14 days)
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

    # Overdue tasks for current user
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
    all_users    = User.objects.filter(is_active=True)
    all_projects = Project.objects.all()
    all_clients  = Client.objects.all()

    ctx = {
        'today': today,
        'active': active,
        'planning': planning,
        'tasks_today': tasks_today,
        'overdue_invoices_count': overdue_invoices_count,
        'cal_events_json': json.dumps(cal_events),
        'active_projects': active_projects,
        'notifications': notifications,
        'all_users': all_users,
        'all_projects': all_projects,
        'all_clients': all_clients,
    }
    return render(request, 'projects/dashboard.html', ctx)


@login_required(login_url=LOGIN_URL)
def project_list(request):
    qs     = Project.objects.all()
    search = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')

    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(client__icontains=search) | Q(location__icontains=search))
    if status:
        qs = qs.filter(status=status)

    totals = Project.objects.aggregate(
        total_budget=Sum('budget'),
        total_spent=Sum('spent'),
    )

    ctx = {
        'projects':      qs,
        'users':         User.objects.all(),
        'search':        search,
        'active_status': status,
        'counts': {
            'all':       Project.objects.count(),
            'active':    Project.objects.filter(status='active').count(),
            'completed': Project.objects.filter(status='completed').count(),
            'planning':  Project.objects.filter(status='planning').count(),
            'paused':    Project.objects.filter(status='paused').count(),
        },
        'total_budget': totals['total_budget'] or 0,
        'total_spent':  totals['total_spent']  or 0,
        'all_clients':  Client.objects.all().values('id', 'name', 'client_type', 'phone', 'company_logo'),
    }
    return render(request, 'projects/project_list.html', ctx)


@login_required(login_url=LOGIN_URL)
def project_create(request):
    if request.method == 'POST':
        p = Project.objects.create(
            name        = request.POST.get('name', '').strip(),
            client      = request.POST.get('client', '').strip(),
            location    = request.POST.get('location', '').strip(),
            description = request.POST.get('description', '').strip(),
            status      = request.POST.get('status', 'planning'),
            progress    = int(request.POST.get('progress', 0) or 0),
            budget      = request.POST.get('budget', 0) or 0,
            spent       = request.POST.get('spent', 0) or 0,
            start_date  = request.POST.get('start_date') or None,
            end_date    = request.POST.get('end_date')   or None,
            manager_id  = request.POST.get('manager')    or None,
        )
        team_ids = request.POST.getlist('team')
        if team_ids:
            p.team.set(team_ids)
        return JsonResponse({'ok': True, 'id': p.id})
    return JsonResponse({'ok': False}, status=400)


@login_required(login_url=LOGIN_URL)
def project_edit(request, pk):
    p = get_object_or_404(Project, pk=pk)
    if request.method == 'GET':
        data = {
            'id': p.id, 'name': p.name, 'client': p.client,
            'location': p.location, 'description': p.description,
            'status': p.status, 'progress': p.progress,
            'budget': str(p.budget), 'spent': str(p.spent),
            'start_date': str(p.start_date) if p.start_date else '',
            'end_date':   str(p.end_date)   if p.end_date   else '',
            'manager': p.manager_id or '',
            'team': list(p.team.values_list('id', flat=True)),
        }
        return JsonResponse(data)
    if request.method == 'POST':
        p.name        = request.POST.get('name', p.name).strip()
        p.client      = request.POST.get('client', '').strip()
        p.location    = request.POST.get('location', '').strip()
        p.description = request.POST.get('description', '').strip()
        p.status      = request.POST.get('status', p.status)
        p.progress    = int(request.POST.get('progress', p.progress) or 0)
        p.budget      = request.POST.get('budget', p.budget) or 0
        p.spent       = request.POST.get('spent', p.spent)   or 0
        p.start_date  = request.POST.get('start_date') or None
        p.end_date    = request.POST.get('end_date')   or None
        p.manager_id  = request.POST.get('manager')    or None
        p.save()
        team_ids = request.POST.getlist('team')
        p.team.set(team_ids)
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False}, status=400)


@login_required(login_url=LOGIN_URL)
def project_delete(request, pk):
    if request.method == 'POST':
        get_object_or_404(Project, pk=pk).delete()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False}, status=400)


@login_required(login_url=LOGIN_URL)
def project_detail(request, pk):
    p     = get_object_or_404(Project, pk=pk)
    tasks = p.tasks.select_related('assigned_to').all()
    users = User.objects.all()
    ctx = {
        'project': p,
        'tasks':   tasks,
        'users':   users,
        'todo':    tasks.filter(status='todo').count(),
        'in_prog': tasks.filter(status='in_progress').count(),
        'done':    tasks.filter(status='done').count(),
    }
    return render(request, 'projects/project_detail.html', ctx)


@login_required(login_url=LOGIN_URL)
def task_create(request, pk):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=pk)
        Task.objects.create(
            project     = project,
            title       = request.POST.get('title', '').strip(),
            status      = request.POST.get('status', 'todo'),
            due_date    = request.POST.get('due_date') or None,
            assigned_to_id = request.POST.get('assigned_to') or None,
        )
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False}, status=400)


@login_required(login_url=LOGIN_URL)
def task_delete(request, pk, task_pk):
    if request.method == 'POST':
        get_object_or_404(Task, pk=task_pk, project_id=pk).delete()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False}, status=400)


@login_required(login_url=LOGIN_URL)
def task_toggle(request, pk, task_pk):
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=task_pk, project_id=pk)
        cycle = {'todo': 'in_progress', 'in_progress': 'done', 'done': 'todo'}
        task.status = cycle.get(task.status, 'todo')
        task.save()
        return JsonResponse({'ok': True, 'status': task.status})
    return JsonResponse({'ok': False}, status=400)


@login_required(login_url=LOGIN_URL)
def task_list(request):
    from django.core.paginator import Paginator
    PAGE_SIZE = 10

    qs = Task.objects.select_related('project', 'assigned_to').all()
    status_filter   = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    project_filter  = request.GET.get('project', '')
    assignee_filter = request.GET.get('assignee', '')
    search          = request.GET.get('q', '').strip()

    if status_filter:
        qs = qs.filter(status=status_filter)
    if priority_filter:
        qs = qs.filter(priority=priority_filter)
    if project_filter:
        qs = qs.filter(project_id=project_filter)
    if assignee_filter:
        qs = qs.filter(assigned_to_id=assignee_filter)
    if search:
        qs = qs.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(assigned_to__first_name__icontains=search) |
            Q(assigned_to__last_name__icontains=search) |
            Q(assigned_to__username__icontains=search)
        )

    today   = timezone.now().date()
    todo    = Task.objects.filter(status='todo').count()
    in_prog = Task.objects.filter(status='in_progress').count()
    done    = Task.objects.filter(status='done').count()
    overdue = Task.objects.filter(due_date__lt=today).exclude(status='done').count()

    paginator = Paginator(qs, PAGE_SIZE)
    page      = paginator.get_page(request.GET.get('page', 1))

    ctx = {
        'tasks': page,
        'page': page,
        'users': User.objects.all(),
        'projects': Project.objects.all(),
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'project_filter': project_filter,
        'assignee_filter': assignee_filter,
        'search': search,
        'todo': todo, 'in_prog': in_prog, 'done': done, 'overdue': overdue,
    }
    return render(request, 'projects/task_list.html', ctx)


@login_required(login_url=LOGIN_URL)
def task_list_create(request):
    if request.method == 'POST':
        t = Task.objects.create(
            project_id  = request.POST.get('project') or None,
            title       = request.POST.get('title', '').strip(),
            description = request.POST.get('description', '').strip(),
            status      = request.POST.get('status', 'todo'),
            priority    = request.POST.get('priority', 'medium'),
            due_date    = request.POST.get('due_date') or None,
            due_time    = _parse_due_time(request.POST),
            assigned_to_id = request.POST.get('assigned_to') or None,
        )
        return JsonResponse({'ok': True, 'id': t.id})
    return JsonResponse({'ok': False}, status=400)


@login_required(login_url=LOGIN_URL)
def task_list_detail(request, pk):
    t = get_object_or_404(Task, pk=pk)
    # AJAX / fetch → return JSON (used by edit panel)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
       'application/json' in request.headers.get('Accept', ''):
        data = {
            'id': t.id,
            'project': t.project_id or '',
            'project_name': t.project.name if t.project else '',
            'title': t.title,
            'description': t.description,
            'status': t.status,
            'priority': t.priority,
            'due_date': str(t.due_date) if t.due_date else '',
            'due_time': t.due_time.strftime('%I:%M %p') if t.due_time else '',
            'due_time_hour': t.due_time.strftime('%I').lstrip('0') or '12' if t.due_time else '',
            'due_time_min': t.due_time.strftime('%M') if t.due_time else '',
            'due_time_ampm': t.due_time.strftime('%p') if t.due_time else '',
            'assigned_to': t.assigned_to_id or '',
        }
        return JsonResponse(data)
    # Normal browser request → render HTML page
    STATUS_MAP = {'todo': 'للتنفيذ', 'in_progress': 'قيد التنفيذ', 'done': 'مكتملة'}
    PRIORITY_MAP = {'low': 'منخفضة', 'medium': 'متوسطة', 'high': 'عالية'}
    return render(request, 'projects/task_detail.html', {
        'task': t,
        'status_ar': STATUS_MAP.get(t.status, t.status),
        'priority_ar': PRIORITY_MAP.get(t.priority, t.priority),
    })


@login_required(login_url=LOGIN_URL)
def task_list_edit(request, pk):
    t = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        t.project_id    = request.POST.get('project') or None
        t.title         = request.POST.get('title', t.title).strip()
        t.description   = request.POST.get('description', '').strip()
        t.status        = request.POST.get('status', t.status)
        t.priority      = request.POST.get('priority', t.priority)
        t.due_date      = request.POST.get('due_date') or None
        t.due_time      = _parse_due_time(request.POST)
        t.assigned_to_id = request.POST.get('assigned_to') or None
        t.save()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False}, status=400)


@login_required(login_url=LOGIN_URL)
def task_list_delete(request, pk):
    if request.method == 'POST':
        get_object_or_404(Task, pk=pk).delete()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False}, status=400)
