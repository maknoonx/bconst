from datetime import date

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group, Permission

from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.utils.crypto import get_random_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.urls import reverse
from .models import Employee
from attendance.models import Overtime
from attendance.filters import filtered_attendance_qs
from company.models import CompanySettings

LOGIN_URL = '/system/'


# ── helpers ──────────────────────────────────────────────────────────────────

def _send_email(to_email, subject, html_body):
    msg = EmailMultiAlternatives(subject=subject, body='', to=[to_email])
    msg.attach_alternative(html_body, 'text/html')
    msg.send()


def _send_password_setup_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    setup_url = request.build_absolute_uri(
        reverse('set_password', kwargs={'uidb64': uid, 'token': token})
    )
    company = CompanySettings.objects.first()
    company_name = (company.company_name_ar if company and company.company_name_ar else 'باء البناء')
    logo_url = request.build_absolute_uri(company.company_logo.url) if company and company.company_logo else None

    html_body = render_to_string('employees/email/password_setup.html', {
        'user': user, 'setup_url': setup_url,
        'company_name': company_name, 'logo_url': logo_url,
    })
    _send_email(user.email, f'إعداد كلمة المرور — {company_name}', html_body)


# ── Employee CRUD ─────────────────────────────────────────────────────────────

@login_required(login_url=LOGIN_URL)
def employee_list(request):
    qs = Employee.objects.select_related('user').all()
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    if q:
        qs = qs.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q) |
            Q(job_title__icontains=q) | Q(phone_number__icontains=q)
        )
    if status:
        qs = qs.filter(status=status)

    # ── attendance log tab ──
    att_employee = request.GET.get('att_employee', '')
    att_from = request.GET.get('att_from', '')
    att_to = request.GET.get('att_to', '')
    att_qs = filtered_attendance_qs(att_employee, att_from, att_to)
    att_page = Paginator(att_qs, 20).get_page(request.GET.get('att_page', 1))

    # ── overtime tab ──
    ot_employee = request.GET.get('ot_employee', '')
    ot_year = request.GET.get('ot_year', '')
    ot_qs = Overtime.objects.select_related('employee').all()
    if ot_employee:
        ot_qs = ot_qs.filter(employee_id=ot_employee)
    if ot_year:
        ot_qs = ot_qs.filter(year=ot_year)
    current_year = date.today().year

    ctx = {
        'employees': qs,
        'all_employees': Employee.objects.order_by('first_name', 'last_name'),
        'users': User.objects.prefetch_related('groups').all(),
        'groups': Group.objects.prefetch_related('permissions', 'user_set').all(),
        'perms': Permission.objects.select_related('content_type').all().order_by('content_type__app_label', 'codename'),
        'q': q, 'status_filter': status,
        'total': Employee.objects.count(),
        'active': Employee.objects.filter(status='A').count(),
        'inactive': Employee.objects.filter(status='U').count(),
        'with_account': Employee.objects.filter(user__isnull=False).count(),

        'att_page': att_page,
        'att_employee_filter': att_employee,
        'att_from': att_from,
        'att_to': att_to,

        'overtime_entries': ot_qs,
        'ot_employee_filter': ot_employee,
        'ot_year_filter': ot_year,
        'ot_years': range(current_year + 1, current_year - 5, -1),
        'ot_months': Overtime.MONTHS,
    }
    return render(request, 'employees/employee_list.html', ctx)


@login_required(login_url=LOGIN_URL)
def employee_create(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=400)
    try:
        e = Employee.objects.create(
            first_name     = request.POST.get('first_name', '').strip(),
            last_name      = request.POST.get('last_name', '').strip(),
            job_title      = request.POST.get('job_title', '').strip(),
            nationality    = request.POST.get('nationality', 'سعودي'),
            gender         = request.POST.get('gender', 'M'),
            id_type        = request.POST.get('id_type', 'NID'),
            id_number      = request.POST.get('id_number', '').strip(),
            date_of_birth  = request.POST.get('date_of_birth') or None,
            employment_date = request.POST.get('employment_date') or None,
            phone_number   = request.POST.get('phone_number', '').strip(),
            email          = request.POST.get('email', '').strip(),
            address        = request.POST.get('address', '').strip(),
            status         = request.POST.get('status', 'A'),
        )
        return JsonResponse({'ok': True, 'id': e.id})
    except Exception as ex:
        return JsonResponse({'ok': False, 'error': str(ex)}, status=400)


@login_required(login_url=LOGIN_URL)
def employee_detail(request, pk):
    e = get_object_or_404(Employee, pk=pk)
    data = {
        'id': e.id,
        'first_name': e.first_name, 'last_name': e.last_name,
        'job_title': e.job_title, 'nationality': e.nationality,
        'gender': e.gender, 'id_type': e.id_type, 'id_number': e.id_number,
        'date_of_birth': str(e.date_of_birth) if e.date_of_birth else '',
        'employment_date': str(e.employment_date) if e.employment_date else '',
        'phone_number': e.phone_number, 'email': e.email, 'address': e.address,
        'status': e.status,
        'user_id': e.user_id or '',
    }
    return JsonResponse(data)


@login_required(login_url=LOGIN_URL)
def employee_edit(request, pk):
    e = get_object_or_404(Employee, pk=pk)
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=400)
    e.first_name     = request.POST.get('first_name', e.first_name).strip()
    e.last_name      = request.POST.get('last_name', e.last_name).strip()
    e.job_title      = request.POST.get('job_title', e.job_title).strip()
    e.nationality    = request.POST.get('nationality', e.nationality)
    e.gender         = request.POST.get('gender', e.gender)
    e.id_type        = request.POST.get('id_type', e.id_type)
    e.id_number      = request.POST.get('id_number', e.id_number).strip()
    e.date_of_birth  = request.POST.get('date_of_birth') or None
    e.employment_date = request.POST.get('employment_date') or None
    e.phone_number   = request.POST.get('phone_number', e.phone_number).strip()
    e.email          = request.POST.get('email', e.email).strip()
    e.address        = request.POST.get('address', e.address).strip()
    e.status         = request.POST.get('status', e.status)
    e.save()
    return JsonResponse({'ok': True})


@login_required(login_url=LOGIN_URL)
def employee_delete(request, pk):
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=400)
    get_object_or_404(Employee, pk=pk).delete()
    return JsonResponse({'ok': True})


@login_required(login_url=LOGIN_URL)
def employee_toggle_status(request, pk):
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=400)
    e = get_object_or_404(Employee, pk=pk)
    e.status = 'U' if e.status == 'A' else 'A'
    e.save()
    return JsonResponse({'ok': True, 'status': e.status})


# ── User CRUD ─────────────────────────────────────────────────────────────────

@login_required(login_url=LOGIN_URL)
def user_create(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=400)
    try:
        employee_id = request.POST.get('employee_id')
        username    = request.POST.get('username', '').strip()
        email       = request.POST.get('email', '').strip()
        group_ids   = request.POST.getlist('groups')
        is_staff    = request.POST.get('is_staff') == '1'

        employee = get_object_or_404(Employee, pk=employee_id)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'ok': False, 'error': 'اسم المستخدم مستخدم مسبقاً'}, status=400)

        user = User.objects.create_user(
            username=username,
            email=email or employee.email,
            first_name=employee.first_name,
            last_name=employee.last_name,
            is_active=False,
            is_staff=is_staff,
            password=get_random_string(32),
        )
        if group_ids:
            user.groups.set(group_ids)

        employee.user = user
        employee.save()

        if user.email:
            try:
                _send_password_setup_email(request, user)
            except Exception:
                pass

        return JsonResponse({'ok': True, 'user_id': user.id})
    except Exception as ex:
        return JsonResponse({'ok': False, 'error': str(ex)}, status=400)


@login_required(login_url=LOGIN_URL)
def user_edit(request, pk):
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=400)
    user = get_object_or_404(User, pk=pk)
    user.is_active = request.POST.get('is_active') == '1'
    user.is_staff  = request.POST.get('is_staff') == '1'
    user.save()
    group_ids = request.POST.getlist('groups')
    user.groups.set(group_ids)
    return JsonResponse({'ok': True})


@login_required(login_url=LOGIN_URL)
def user_delete(request, pk):
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=400)
    user = get_object_or_404(User, pk=pk)
    # unlink employee profile
    if hasattr(user, 'employee_profile'):
        user.employee_profile.user = None
        user.employee_profile.save()
    user.delete()
    return JsonResponse({'ok': True})


@login_required(login_url=LOGIN_URL)
def user_resend_email(request, pk):
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=400)
    user = get_object_or_404(User, pk=pk)
    try:
        _send_password_setup_email(request, user)
        return JsonResponse({'ok': True})
    except Exception as ex:
        return JsonResponse({'ok': False, 'error': str(ex)}, status=400)


# ── Group CRUD ────────────────────────────────────────────────────────────────

@login_required(login_url=LOGIN_URL)
def group_create(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=400)
    name = request.POST.get('name', '').strip()
    perm_ids = request.POST.getlist('permissions')
    if not name:
        return JsonResponse({'ok': False, 'error': 'اسم المجموعة مطلوب'}, status=400)
    g = Group.objects.create(name=name)
    if perm_ids:
        g.permissions.set(perm_ids)
    return JsonResponse({'ok': True, 'id': g.id, 'name': g.name})


@login_required(login_url=LOGIN_URL)
def group_detail(request, pk):
    g = get_object_or_404(Group, pk=pk)
    return JsonResponse({
        'id': g.id, 'name': g.name,
        'permissions': list(g.permissions.values_list('id', flat=True)),
    })


@login_required(login_url=LOGIN_URL)
def group_edit(request, pk):
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=400)
    g = get_object_or_404(Group, pk=pk)
    g.name = request.POST.get('name', g.name).strip()
    g.save()
    perm_ids = request.POST.getlist('permissions')
    g.permissions.set(perm_ids)
    return JsonResponse({'ok': True})


@login_required(login_url=LOGIN_URL)
def group_delete(request, pk):
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=400)
    get_object_or_404(Group, pk=pk).delete()
    return JsonResponse({'ok': True})


# ── Set password (from email link) ────────────────────────────────────────────

def set_password(request, uidb64, token):
    try:
        uid  = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return render(request, 'employees/set_password.html', {'invalid': True})

    if not default_token_generator.check_token(user, token):
        return render(request, 'employees/set_password.html', {'invalid': True})

    if request.method == 'POST':
        p1 = request.POST.get('password1', '')
        p2 = request.POST.get('password2', '')
        if p1 != p2:
            return render(request, 'employees/set_password.html', {'error': 'كلمتا المرور غير متطابقتين', 'user': user})
        try:
            validate_password(p1, user)
        except ValidationError as ex:
            return render(request, 'employees/set_password.html', {'error': ' '.join(ex.messages), 'user': user})
        user.set_password(p1)
        user.is_active = True
        user.save()
        return render(request, 'employees/set_password.html', {'success': True})

    return render(request, 'employees/set_password.html', {'user': user})
