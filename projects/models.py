from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    STATUS_CHOICES = [
        ('active',    'نشط'),
        ('completed', 'مكتمل'),
        ('paused',    'متوقف'),
        ('planning',  'تخطيط'),
    ]

    name        = models.CharField(max_length=200, verbose_name='اسم المشروع')
    description = models.TextField(blank=True, verbose_name='الوصف')
    client      = models.CharField(max_length=150, blank=True, verbose_name='العميل')
    location    = models.CharField(max_length=200, blank=True, verbose_name='الموقع')
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning', verbose_name='الحالة')
    progress    = models.PositiveIntegerField(default=0, verbose_name='نسبة الإنجاز %')
    budget      = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='الميزانية (ريال)')
    spent       = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='المصروف (ريال)')
    start_date  = models.DateField(null=True, blank=True, verbose_name='تاريخ البدء')
    end_date    = models.DateField(null=True, blank=True, verbose_name='تاريخ الانتهاء')
    manager     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='managed_projects', verbose_name='مدير المشروع')
    team        = models.ManyToManyField(User, blank=True, related_name='projects', verbose_name='الفريق')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'مشروع'
        verbose_name_plural = 'المشاريع'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def budget_percent(self):
        if self.budget > 0:
            return min(int((self.spent / self.budget) * 100), 100)
        return 0


class Task(models.Model):
    STATUS_CHOICES = [
        ('todo',        'لم تبدأ'),
        ('in_progress', 'جارية'),
        ('done',        'مكتملة'),
    ]
    PRIORITY_CHOICES = [
        ('low',    'منخفضة'),
        ('medium', 'متوسطة'),
        ('high',   'عالية'),
        ('urgent', 'عاجلة'),
    ]
    project     = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    title       = models.CharField(max_length=300, verbose_name='المهمة')
    description = models.TextField(blank=True, verbose_name='الوصف')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='المسؤول')
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority    = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    due_date    = models.DateField(null=True, blank=True)
    due_time    = models.TimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'مهمة'
        verbose_name_plural = 'المهام'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.due_date and self.due_date < timezone.now().date() and self.status != 'done'
