from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User


class Employee(models.Model):
    ID_TYPES = [
        ('NID', 'هوية وطنية'),
        ('IQA', 'إقامة'),
        ('PAS', 'جواز سفر'),
    ]
    GENDER = [
        ('M', 'ذكر'),
        ('F', 'أنثى'),
    ]
    STATUS = [
        ('A', 'نشط'),
        ('U', 'غير نشط'),
    ]
    NATIONALITIES = [
        ('سعودي', 'سعودي'),
        ('مقيم', 'مقيم'),
        ('مصري', 'مصري'),
        ('يمني', 'يمني'),
        ('باكستاني', 'باكستاني'),
        ('هندي', 'هندي'),
        ('بنغلاديشي', 'بنغلاديشي'),
        ('فلبيني', 'فلبيني'),
        ('سوداني', 'سوداني'),
        ('سوري', 'سوري'),
        ('أردني', 'أردني'),
        ('لبناني', 'لبناني'),
        ('عراقي', 'عراقي'),
        ('تركي', 'تركي'),
        ('إندونيسي', 'إندونيسي'),
        ('إثيوبي', 'إثيوبي'),
        ('أخرى', 'أخرى'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='employee_profile', verbose_name='حساب النظام'
    )
    first_name     = models.CharField(max_length=100, verbose_name='الاسم الأول')
    last_name      = models.CharField(max_length=100, verbose_name='اسم العائلة')
    job_title      = models.CharField(max_length=150, verbose_name='المسمى الوظيفي')
    nationality    = models.CharField(max_length=50, choices=NATIONALITIES, default='سعودي', verbose_name='الجنسية')
    gender         = models.CharField(max_length=1, choices=GENDER, default='M', verbose_name='الجنس')
    id_type        = models.CharField(max_length=3, choices=ID_TYPES, default='NID', verbose_name='نوع الإثبات')
    id_number      = models.CharField(max_length=50, verbose_name='رقم الإثبات')
    date_of_birth  = models.DateField(null=True, blank=True, verbose_name='تاريخ الميلاد')
    employment_date = models.DateField(null=True, blank=True, verbose_name='تاريخ التوظيف')

    phone_regex = RegexValidator(
        regex=r'^\+?[\d\s\-]{7,15}$',
        message='رقم جوال غير صحيح'
    )
    phone_number = models.CharField(max_length=20, blank=True, verbose_name='رقم الجوال')
    email        = models.EmailField(blank=True, verbose_name='البريد الإلكتروني')
    address      = models.CharField(max_length=255, blank=True, verbose_name='العنوان')
    status       = models.CharField(max_length=1, choices=STATUS, default='A', verbose_name='الحالة')

    profile_picture = models.ImageField(
        upload_to='employees/photos/', null=True, blank=True, verbose_name='الصورة الشخصية'
    )

    class Meta:
        verbose_name = 'موظف'
        verbose_name_plural = 'الموظفين'
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def initials(self):
        parts = [self.first_name, self.last_name]
        return ''.join(p[0].upper() for p in parts if p)
