from django.db import models
from django.contrib.auth.models import User
from employees.models import Employee


class AttendanceRecord(models.Model):
    TYPE_CHOICES = [
        ('IN', 'حضور'),
        ('OUT', 'انصراف'),
    ]

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='attendance_records', verbose_name='الموظف'
    )
    record_type = models.CharField(max_length=3, choices=TYPE_CHOICES, verbose_name='النوع')
    photo = models.ImageField(
        upload_to='attendance/photos/%Y/%m/', null=True, blank=True, verbose_name='الصورة'
    )
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name='خط العرض')
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name='خط الطول')
    note = models.TextField(blank=True, verbose_name='ملاحظة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='الوقت')

    paired_check_in = models.OneToOneField(
        'self', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='paired_check_out', verbose_name='الحضور المرتبط'
    )

    is_approved = models.BooleanField(default=False, verbose_name='معتمد')
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ الاعتماد')
    approved_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='+', verbose_name='اعتمد بواسطة'
    )

    class Meta:
        verbose_name = 'سجل حضور وانصراف'
        verbose_name_plural = 'سجلات الحضور والانصراف'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.employee.full_name} - {self.get_record_type_display()} - {self.created_at:%Y-%m-%d %H:%M}'

    @property
    def has_location(self):
        return self.latitude is not None and self.longitude is not None

    @property
    def map_url(self):
        if self.has_location:
            return f'https://www.google.com/maps?q={self.latitude},{self.longitude}'
        return ''

    @property
    def work_hours(self):
        if self.record_type == 'OUT' and self.paired_check_in_id:
            delta = self.created_at - self.paired_check_in.created_at
            return round(delta.total_seconds() / 3600, 2)
        return None


class Overtime(models.Model):
    MONTHS = [
        (1, 'يناير'), (2, 'فبراير'), (3, 'مارس'), (4, 'أبريل'),
        (5, 'مايو'), (6, 'يونيو'), (7, 'يوليو'), (8, 'أغسطس'),
        (9, 'سبتمبر'), (10, 'أكتوبر'), (11, 'نوفمبر'), (12, 'ديسمبر'),
    ]

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='overtime_entries', verbose_name='الموظف'
    )
    month = models.PositiveSmallIntegerField(choices=MONTHS, verbose_name='الشهر')
    year = models.PositiveSmallIntegerField(verbose_name='السنة')
    hours = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='عدد الساعات')
    note = models.CharField(max_length=255, blank=True, verbose_name='ملاحظة')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='+', verbose_name='أضيف بواسطة'
    )

    class Meta:
        verbose_name = 'وقت إضافي'
        verbose_name_plural = 'الأوقات الإضافية'
        ordering = ['-year', '-month', 'employee__first_name']

    def __str__(self):
        return f'{self.employee.full_name} - {self.get_month_display()} {self.year} - {self.hours}س'
