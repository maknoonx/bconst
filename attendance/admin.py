from django.contrib import admin
from .models import AttendanceRecord, Overtime


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('employee', 'record_type', 'created_at', 'is_approved')
    list_filter = ('record_type', 'is_approved')
    search_fields = ('employee__first_name', 'employee__last_name')


@admin.register(Overtime)
class OvertimeAdmin(admin.ModelAdmin):
    list_display = ('employee', 'month', 'year', 'hours')
    list_filter = ('year', 'month')
    search_fields = ('employee__first_name', 'employee__last_name')
