from .models import AttendanceRecord


def filtered_attendance_qs(employee_id='', date_from='', date_to=''):
    qs = AttendanceRecord.objects.select_related('employee', 'paired_check_in').all()
    if employee_id:
        qs = qs.filter(employee_id=employee_id)
    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__date__lte=date_to)
    return qs
