from django.db import models
from django.contrib.auth.models import User


class MonthlyPlan(models.Model):
    STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('approved', 'معتمدة'),
        ('completed', 'مكتملة'),
    ]
    title      = models.CharField(max_length=200)
    month      = models.DateField()
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes      = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-month']

    def __str__(self):
        return f"{self.title} — {self.month.strftime('%Y/%m')}"

    @property
    def total_budget(self):
        return sum(b.amount for b in self.budgets.all())


class PlanObjective(models.Model):
    plan   = models.ForeignKey(MonthlyPlan, on_delete=models.CASCADE, related_name='objectives')
    title  = models.CharField(max_length=200)
    goal   = models.TextField(blank=True)
    result = models.TextField(blank=True)
    order  = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']


class PlanBudget(models.Model):
    plan        = models.ForeignKey(MonthlyPlan, on_delete=models.CASCADE, related_name='budgets')
    budget_type = models.CharField(max_length=100)
    amount      = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    order       = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']


class PlanChannel(models.Model):
    plan  = models.ForeignKey(MonthlyPlan, on_delete=models.CASCADE, related_name='channels')
    name  = models.CharField(max_length=100)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']


class PlanChannelDay(models.Model):
    channel  = models.ForeignKey(PlanChannel, on_delete=models.CASCADE, related_name='days')
    day_date = models.DateField()
    content  = models.TextField(blank=True)

    class Meta:
        ordering = ['day_date']


class PlanTarget(models.Model):
    TARGET_TYPE_CHOICES = [
        ('revenue',   'إيرادات'),
        ('contracts', 'عقود'),
        ('leads',     'عملاء محتملون'),
        ('projects',  'مشاريع'),
        ('general',   'عام'),
    ]
    plan         = models.ForeignKey(MonthlyPlan, on_delete=models.CASCADE, related_name='targets')
    target_type  = models.CharField(max_length=30, choices=TARGET_TYPE_CHOICES, default='general')
    label        = models.CharField(max_length=200, blank=True)
    target_value = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    result_value = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    order        = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']


class ExternalMarketer(models.Model):
    SCHEDULE_CHOICES = [
        ('monthly',   'شهري'),
        ('quarterly', 'ربع سنوي'),
        ('project',   'بالمشروع'),
    ]
    name                = models.CharField(max_length=200)
    phone               = models.CharField(max_length=20, blank=True)
    email               = models.EmailField(blank=True)
    bank                = models.CharField(max_length=100, blank=True)
    iban                = models.CharField(max_length=34, blank=True)
    commission_rate     = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    settlement_schedule = models.CharField(max_length=20, choices=SCHEDULE_CHOICES, default='monthly')
    is_active           = models.BooleanField(default=True)
    notes               = models.TextField(blank=True)
    created_at          = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
