from django.db import models


class Client(models.Model):
    TYPE_INDIVIDUAL = 'individual'
    TYPE_COMPANY = 'company'
    TYPE_CHOICES = [
        (TYPE_INDIVIDUAL, 'فرد'),
        (TYPE_COMPANY, 'شركة'),
    ]

    client_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_INDIVIDUAL, verbose_name='نوع العميل')
    name = models.CharField(max_length=200, verbose_name='الاسم')
    phone = models.CharField(max_length=20, blank=True, verbose_name='رقم الجوال')
    email = models.EmailField(blank=True, verbose_name='البريد الإلكتروني')
    address = models.TextField(blank=True, verbose_name='العنوان')
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Individual fields
    national_id = models.CharField(max_length=20, blank=True, verbose_name='رقم الهوية')

    # Company fields
    company_logo = models.ImageField(upload_to='clients/logos/', blank=True, null=True, verbose_name='شعار الشركة')
    tax_number = models.CharField(max_length=50, blank=True, verbose_name='الرقم الضريبي')
    commercial_registration = models.CharField(max_length=50, blank=True, verbose_name='السجل التجاري')
    contact_person = models.CharField(max_length=100, blank=True, verbose_name='الشخص المسؤول')
    contact_person_title = models.CharField(max_length=100, blank=True, verbose_name='المسمى الوظيفي')
    website = models.URLField(blank=True, verbose_name='الموقع الإلكتروني')

    class Meta:
        verbose_name = 'عميل'
        verbose_name_plural = 'العملاء'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def is_company(self):
        return self.client_type == self.TYPE_COMPANY

    @property
    def type_label(self):
        return 'شركة' if self.is_company else 'فرد'
