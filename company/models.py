from django.db import models


class CompanySettings(models.Model):
    company_logo    = models.ImageField(upload_to='company/', blank=True, null=True)
    company_name_ar = models.CharField(max_length=255, blank=True)
    company_name_en = models.CharField(max_length=255, blank=True)
    unified_number  = models.CharField(max_length=20, blank=True)
    cr_number       = models.CharField(max_length=20, blank=True)
    cr_issue_date   = models.DateField(blank=True, null=True)
    municipality_license = models.CharField(max_length=100, blank=True)
    tax_registration_number = models.CharField(max_length=50, blank=True)
    facility_address     = models.TextField(blank=True)
    address_building_number = models.CharField(max_length=20, blank=True)
    address_street       = models.CharField(max_length=255, blank=True)
    address_district     = models.CharField(max_length=255, blank=True)
    address_city         = models.CharField(max_length=100, blank=True)
    address_postal_code  = models.CharField(max_length=10, blank=True)
    manager_name        = models.CharField(max_length=255, blank=True)
    manager_nationality = models.CharField(max_length=100, blank=True)
    manager_id          = models.CharField(max_length=50, blank=True)
    manager_mobile      = models.CharField(max_length=20, blank=True)
    manager_email       = models.EmailField(blank=True)
    pr_mobile         = models.CharField(max_length=20, blank=True)
    pr_email          = models.EmailField(blank=True)
    marketing_mobile  = models.CharField(max_length=20, blank=True)
    marketing_email   = models.EmailField(blank=True)
    hr_email          = models.EmailField(blank=True)
    instagram      = models.URLField(blank=True)
    tiktok         = models.URLField(blank=True)
    facebook       = models.URLField(blank=True)
    youtube        = models.URLField(blank=True)
    twitter        = models.URLField(blank=True)
    snapchat       = models.URLField(blank=True)
    google_maps_link = models.URLField(blank=True)
    website_link   = models.URLField(blank=True)

    class Meta:
        verbose_name = 'إعدادات الشركة'

    def __str__(self):
        return self.company_name_ar or self.company_name_en or 'إعدادات الشركة'


class PaymentMethod(models.Model):
    TYPE_CHOICES = [('immediate', 'فوري'), ('deferred', 'آجل')]
    name         = models.CharField(max_length=100, verbose_name='اسم طريقة الدفع')
    payment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='immediate', verbose_name='نوع الدفع')
    company_name = models.CharField(max_length=100, blank=True, verbose_name='اسم الشركة')
    fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='نسبة الرسوم %')
    fixed_fee    = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='الرسوم الثابتة')
    notes        = models.TextField(blank=True, verbose_name='ملاحظات')
    is_active    = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'طريقة دفع'
        verbose_name_plural = 'طرق الدفع'

    def __str__(self):
        return self.name


class CompanyDocument(models.Model):
    TYPE_CHOICES = [('license', 'ترخيص'), ('contract', 'عقد'), ('document', 'مستند عام')]
    file_type  = models.CharField(max_length=20, choices=TYPE_CHOICES, default='document')
    file_name  = models.CharField(max_length=255)
    file       = models.FileField(upload_to='company/docs/', blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date   = models.DateField(blank=True, null=True)
    notes      = models.TextField(blank=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.file_name
