from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from employees.models import Employee
from bconstproject.validators import validate_uploaded_image
from .models import AttendanceRecord, Overtime
from .filters import filtered_attendance_qs

LOGIN_URL = '/system/'


def _current_employee(request):
    return getattr(request.user, 'employee_profile', None)


@login_required(login_url=LOGIN_URL)
def checkin_page(request):
    employee = _current_employee(request)
    today_records = []
    if employee:
        today_records = AttendanceRecord.objects.filter(
            employee=employee, created_at__date=timezone.localdate()
        ).order_by('created_at')
    return render(request, 'attendance/checkin.html', {
        'employee': employee,
        'today_records': today_records,
    })


@login_required(login_url=LOGIN_URL)
def record_create(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=400)

    employee = _current_employee(request)
    if not employee:
        return JsonResponse({'ok': False, 'error': 'لا يوجد ملف موظف مرتبط بحسابك'}, status=400)

    record_type = request.POST.get('record_type')
    if record_type not in ('IN', 'OUT'):
        return JsonResponse({'ok': False, 'error': 'نوع تسجيل غير صحيح'}, status=400)

    photo = request.FILES.get('photo')
    if not photo:
        return JsonResponse({'ok': False, 'error': 'صورة التوثيق مطلوبة'}, status=400)
    error = validate_uploaded_image(photo)
    if error:
        return JsonResponse({'ok': False, 'error': error}, status=400)

    def _parse_coord(val):
        try:
            return Decimal(str(val))
        except (InvalidOperation, TypeError, ValueError):
            return None

    latitude = _parse_coord(request.POST.get('latitude'))
    longitude = _parse_coord(request.POST.get('longitude'))
    note = request.POST.get('note', '').strip()

    record = AttendanceRecord.objects.create(
        employee=employee,
        record_type=record_type,
        photo=photo,
        latitude=latitude,
        longitude=longitude,
        note=note,
    )

    if record_type == 'OUT':
        last_in = AttendanceRecord.objects.filter(
            employee=employee, record_type='IN', paired_check_out__isnull=True
        ).order_by('-created_at').first()
        if last_in:
            record.paired_check_in = last_in
            record.save(update_fields=['paired_check_in'])

    return JsonResponse({
        'ok': True,
        'id': record.id,
        'record_type': record.record_type,
        'created_at': timezone.localtime(record.created_at).strftime('%H:%M'),
        'work_hours': record.work_hours,
    })


@login_required(login_url=LOGIN_URL)
def approve_record(request, pk):
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=400)
    record = get_object_or_404(AttendanceRecord, pk=pk)
    if not record.is_approved:
        if record.photo:
            record.photo.delete(save=False)
            record.photo = None
        record.is_approved = True
        record.approved_at = timezone.now()
        record.approved_by = request.user
        record.save()
    return JsonResponse({'ok': True})


@login_required(login_url=LOGIN_URL)
def approve_bulk(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=400)
    qs = filtered_attendance_qs(
        employee_id=request.POST.get('employee', ''),
        date_from=request.POST.get('date_from', ''),
        date_to=request.POST.get('date_to', ''),
    ).filter(is_approved=False)

    count = 0
    for record in qs:
        if record.photo:
            record.photo.delete(save=False)
            record.photo = None
        record.is_approved = True
        record.approved_at = timezone.now()
        record.approved_by = request.user
        record.save()
        count += 1

    return JsonResponse({'ok': True, 'count': count})


@login_required(login_url=LOGIN_URL)
def overtime_create(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=400)
    try:
        employee = get_object_or_404(Employee, pk=request.POST.get('employee'))
        Overtime.objects.create(
            employee=employee,
            month=int(request.POST.get('month')),
            year=int(request.POST.get('year')),
            hours=Decimal(request.POST.get('hours', '0') or '0'),
            note=request.POST.get('note', '').strip(),
            created_by=request.user,
        )
        return JsonResponse({'ok': True})
    except (TypeError, ValueError, InvalidOperation):
        return JsonResponse({'ok': False, 'error': 'بيانات غير صحيحة'}, status=400)


@login_required(login_url=LOGIN_URL)
def overtime_delete(request, pk):
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=400)
    get_object_or_404(Overtime, pk=pk).delete()
    return JsonResponse({'ok': True})
