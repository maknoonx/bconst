from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class AccountType(models.Model):
    CATEGORY_CHOICES = [
        ('asset',     'أصول'),
        ('liability', 'خصوم'),
        ('equity',    'حقوق ملكية'),
        ('revenue',   'إيرادات'),
        ('expense',   'مصروفات'),
    ]
    NORMAL_BALANCE_CHOICES = [
        ('debit',  'مدين'),
        ('credit', 'دائن'),
    ]
    category       = models.CharField(max_length=20, choices=CATEGORY_CHOICES, unique=True, verbose_name='التصنيف')
    normal_balance = models.CharField(max_length=10, choices=NORMAL_BALANCE_CHOICES, verbose_name='الرصيد الطبيعي')

    def __str__(self):
        return self.get_category_display()

    class Meta:
        verbose_name = 'نوع الحساب'
        verbose_name_plural = 'أنواع الحسابات'


class Account(models.Model):
    code         = models.CharField(max_length=20, unique=True, verbose_name='رقم الحساب')
    name         = models.CharField(max_length=200, verbose_name='اسم الحساب')
    account_type = models.ForeignKey(AccountType, on_delete=models.PROTECT, related_name='accounts', verbose_name='نوع الحساب')
    parent       = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT, related_name='children', verbose_name='الحساب الرئيسي')
    is_active    = models.BooleanField(default=True, verbose_name='نشط')
    is_system    = models.BooleanField(default=False, verbose_name='حساب نظام')
    notes        = models.TextField(blank=True, verbose_name='ملاحظات')

    def __str__(self):
        return f'{self.code} - {self.name}'

    def get_balance(self):
        from django.db.models.functions import Coalesce
        result = self.journal_lines.filter(journal__is_posted=True).aggregate(
            total_debit=Coalesce(models.Sum('debit'), Decimal('0')),
            total_credit=Coalesce(models.Sum('credit'), Decimal('0')),
        )
        debit  = result['total_debit']
        credit = result['total_credit']
        if self.account_type.normal_balance == 'debit':
            return debit - credit
        return credit - debit

    class Meta:
        verbose_name = 'حساب'
        verbose_name_plural = 'دليل الحسابات'
        ordering = ['code']


class CostCenter(models.Model):
    TYPE_CHOICES = [
        ('project', 'مشروع'),
        ('admin',   'إدارة'),
        ('shared',  'مشترك'),
    ]
    name = models.CharField(max_length=100, verbose_name='الاسم')
    code = models.CharField(max_length=20, unique=True, verbose_name='الرمز')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='project', verbose_name='النوع')

    def __str__(self):
        return f'{self.code} - {self.name}'

    class Meta:
        verbose_name = 'مركز تكلفة'
        verbose_name_plural = 'مراكز التكلفة'


class Journal(models.Model):
    SOURCE_CHOICES = [
        ('invoice',      'فاتورة'),
        ('receipt',      'سند قبض'),
        ('purchase',     'مشتريات'),
        ('payment',      'دفعة'),
        ('payroll',      'رواتب'),
        ('depreciation', 'استهلاك'),
        ('manual',       'قيد يدوي'),
    ]
    number      = models.CharField(max_length=30, unique=True, editable=False, verbose_name='رقم القيد')
    date        = models.DateField(verbose_name='التاريخ')
    description = models.CharField(max_length=500, verbose_name='البيان')
    source_type = models.CharField(max_length=30, choices=SOURCE_CHOICES, default='manual', verbose_name='نوع المصدر')
    cost_center = models.ForeignKey(CostCenter, null=True, blank=True, on_delete=models.SET_NULL, related_name='journals', verbose_name='مركز التكلفة')
    is_posted   = models.BooleanField(default=False, verbose_name='معتمد')
    created_by  = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='journals', verbose_name='أنشأه')
    created_at  = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.number:
            last = Journal.objects.order_by('-id').first()
            seq  = (last.id + 1) if last else 1
            self.number = f'JV-{seq:06d}'
        super().save(*args, **kwargs)

    def get_total_debit(self):
        return self.lines.aggregate(t=models.Sum('debit'))['t'] or Decimal('0')

    def get_total_credit(self):
        return self.lines.aggregate(t=models.Sum('credit'))['t'] or Decimal('0')

    def is_balanced(self):
        return self.get_total_debit() == self.get_total_credit()

    def post(self):
        if not self.is_balanced():
            raise ValidationError('القيد غير متوازن — لا يمكن اعتماده.')
        self.is_posted = True
        self.save()

    def __str__(self):
        return f'{self.number} | {self.date} | {self.description}'

    class Meta:
        verbose_name = 'قيد يومية'
        verbose_name_plural = 'قيود اليومية'
        ordering = ['-date', '-id']


class JournalLine(models.Model):
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name='lines', verbose_name='القيد')
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='journal_lines', verbose_name='الحساب')
    debit   = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='مدين')
    credit  = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='دائن')
    note    = models.CharField(max_length=300, blank=True, verbose_name='ملاحظة')

    def clean(self):
        if self.debit < 0 or self.credit < 0:
            raise ValidationError('المبالغ يجب أن تكون موجبة.')
        if self.debit > 0 and self.credit > 0:
            raise ValidationError('لا يجوز أن يكون السطر مديناً ودائناً في آن واحد.')

    def __str__(self):
        return f'{self.account} | د:{self.debit} | ك:{self.credit}'

    class Meta:
        verbose_name = 'سطر قيد'
        verbose_name_plural = 'سطور القيود'


class FixedAsset(models.Model):
    CATEGORY_CHOICES = [
        ('heavy_equipment', 'معدات ثقيلة'),
        ('vehicles',        'مركبات'),
        ('tools',           'أدوات وعدد'),
        ('it_equipment',    'معدات تقنية'),
        ('furniture',       'أثاث'),
        ('other',           'أخرى'),
    ]
    name               = models.CharField(max_length=200, verbose_name='اسم الأصل')
    category           = models.CharField(max_length=30, choices=CATEGORY_CHOICES, verbose_name='الفئة')
    purchase_date      = models.DateField(verbose_name='تاريخ الشراء')
    cost               = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='التكلفة الأصلية')
    useful_life_months = models.PositiveIntegerField(verbose_name='العمر الافتراضي (أشهر)')
    salvage_value      = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='القيمة التخريدية')
    cost_center        = models.ForeignKey(CostCenter, null=True, blank=True, on_delete=models.SET_NULL, related_name='fixed_assets', verbose_name='مركز التكلفة')
    is_active          = models.BooleanField(default=True, verbose_name='نشط')
    notes              = models.TextField(blank=True, verbose_name='ملاحظات')

    def monthly_depreciation(self):
        depreciable = self.cost - self.salvage_value
        if self.useful_life_months <= 0:
            return Decimal('0')
        return (depreciable / self.useful_life_months).quantize(Decimal('0.01'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'أصل ثابت'
        verbose_name_plural = 'الأصول الثابتة'


class AccountingPeriod(models.Model):
    STATUS_CHOICES = [
        ('open',   'مفتوحة'),
        ('closed', 'مقفلة'),
    ]
    year      = models.PositiveIntegerField(verbose_name='السنة')
    month     = models.PositiveIntegerField(verbose_name='الشهر')
    status    = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open', verbose_name='الحالة')
    closed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='closed_periods', verbose_name='أقفلها')
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ الإقفال')

    def is_locked(self):
        return self.status == 'closed'

    def __str__(self):
        return f'{self.year}/{self.month:02d} — {self.get_status_display()}'

    class Meta:
        unique_together = [('year', 'month')]
        verbose_name = 'فترة محاسبية'
        verbose_name_plural = 'الفترات المحاسبية'
        ordering = ['-year', '-month']


class PayrollRun(models.Model):
    STATUS_CHOICES = [
        ('draft',  'مسودة'),
        ('posted', 'مرحّل'),
        ('void',   'ملغى'),
    ]
    year        = models.PositiveIntegerField(verbose_name='السنة')
    month       = models.PositiveIntegerField(verbose_name='الشهر')
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name='الحالة')
    total_gross = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='إجمالي الرواتب')
    total_net   = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='صافي المدفوع')
    created_by  = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='أنشأه')
    created_at  = models.DateTimeField(auto_now_add=True)
    notes       = models.TextField(blank=True, verbose_name='ملاحظات')

    def __str__(self):
        return f'مسير رواتب {self.year}/{self.month:02d}'

    class Meta:
        unique_together = [('year', 'month')]
        verbose_name = 'مسير رواتب'
        verbose_name_plural = 'مسيرات الرواتب'
        ordering = ['-year', '-month']


class PayrollLine(models.Model):
    payroll        = models.ForeignKey(PayrollRun, on_delete=models.CASCADE, related_name='lines', verbose_name='المسير')
    employee       = models.ForeignKey('employees.Employee', on_delete=models.PROTECT, verbose_name='الموظف')
    basic          = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='الراتب الأساسي')
    allowances     = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='البدلات')
    deductions     = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='الاستقطاعات')
    deduction_note = models.CharField(max_length=255, blank=True, verbose_name='سبب الاستقطاع')
    bonus          = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='البونص')
    bonus_note     = models.CharField(max_length=255, blank=True, verbose_name='سبب البونص')

    @property
    def gross(self):
        return self.basic + self.allowances

    @property
    def net(self):
        return self.gross + self.bonus - self.deductions

    def __str__(self):
        return f'{self.employee} — {self.payroll}'

    class Meta:
        unique_together = [('payroll', 'employee')]
        verbose_name = 'سطر مسير'
        verbose_name_plural = 'سطور المسير'
