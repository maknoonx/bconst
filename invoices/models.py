from django.db import models
from django.contrib.auth.models import User
from datetime import date


class ServiceCategory(models.Model):
    name       = models.CharField(max_length=100, unique=True, verbose_name='اسم التصنيف')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'تصنيف خدمة'
        verbose_name_plural = 'تصنيفات الخدمات'

    def __str__(self):
        return self.name


class Service(models.Model):
    name          = models.CharField(max_length=255, verbose_name='اسم الخدمة')
    description   = models.TextField(blank=True, verbose_name='الوصف التفصيلي')
    unit          = models.CharField(max_length=50, blank=True, verbose_name='الوحدة')
    default_price = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name='السعر الافتراضي')
    category      = models.CharField(max_length=100, blank=True, verbose_name='التصنيف')
    is_active     = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']
        verbose_name = 'خدمة'
        verbose_name_plural = 'الخدمات'

    def __str__(self):
        return self.name


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft',        'مسودة'),
        ('final',        'نهائية'),
        ('partial_paid', 'مدفوعة جزئياً'),
        ('fully_paid',   'مدفوعة بالكامل'),
        ('cancelled',    'ملغاة'),
    ]

    invoice_number  = models.CharField(max_length=50, unique=True, editable=False)
    issue_date      = models.DateField(default=date.today, db_index=True)
    due_date        = models.DateField(blank=True, null=True, db_index=True)
    client          = models.ForeignKey('clients.Client', on_delete=models.PROTECT, related_name='invoices')
    project         = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    subtotal        = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    vat_rate        = models.DecimalField(max_digits=5, decimal_places=2, default=15)
    vat_amount      = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_amount    = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    paid_amount     = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    notes           = models.TextField(blank=True)
    created_by      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.invoice_number

    @property
    def remaining_amount(self):
        return self.total_amount - self.paid_amount

    @property
    def credit_total(self):
        from decimal import Decimal
        return sum((n.amount for n in self.invoice_notes.filter(note_type='credit')), Decimal('0'))

    @property
    def debit_total(self):
        from decimal import Decimal
        return sum((n.amount for n in self.invoice_notes.filter(note_type='debit')), Decimal('0'))

    @property
    def refund_total(self):
        from decimal import Decimal
        return sum((n.amount for n in self.invoice_notes.filter(note_type='refund')), Decimal('0'))

    @property
    def adjusted_total(self):
        return self.total_amount - self.credit_total + self.debit_total

    @property
    def adjusted_remaining(self):
        return self.adjusted_total - (self.paid_amount - self.refund_total)

    def recalculate(self):
        from decimal import Decimal
        self.subtotal        = sum(l.total for l in self.lines.all())
        net                  = self.subtotal - self.discount_amount
        self.vat_amount      = (net * self.vat_rate / Decimal('100')).quantize(Decimal('0.01'))
        self.total_amount    = (net + self.vat_amount).quantize(Decimal('0.01'))
        self.paid_amount     = sum(r.amount for r in self.receipts.all())
        if self.paid_amount <= 0:
            if self.status not in ('draft', 'final', 'cancelled'):
                self.status = 'final'
        elif self.paid_amount >= self.total_amount:
            self.status = 'fully_paid'
        else:
            self.status = 'partial_paid'
        self.save()

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last = Invoice.objects.order_by('-id').first()
            n    = (last.id + 1) if last else 1
            self.invoice_number = f'INV-{n:05d}'
        super().save(*args, **kwargs)


class InvoiceLine(models.Model):
    invoice     = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='lines')
    description = models.CharField(max_length=500)
    qty         = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit        = models.CharField(max_length=50, blank=True)
    unit_price  = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total       = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.total = self.qty * self.unit_price
        super().save(*args, **kwargs)


class PaymentReceipt(models.Model):
    METHOD_CHOICES = [
        ('cash',     'نقداً'),
        ('transfer', 'تحويل بنكي'),
        ('check',    'شيك'),
        ('card',     'بطاقة'),
        ('other',    'أخرى'),
    ]

    invoice        = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='receipts')
    receipt_number = models.CharField(max_length=50, unique=True, editable=False)
    amount         = models.DecimalField(max_digits=14, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='cash')
    payment_date   = models.DateField(default=date.today)
    notes          = models.TextField(blank=True)
    created_by     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            last = PaymentReceipt.objects.order_by('-id').first()
            n    = (last.id + 1) if last else 1
            self.receipt_number = f'REC-{n:05d}'
        super().save(*args, **kwargs)
        self.invoice.recalculate()

    class Meta:
        ordering = ['-payment_date']


# ──────────────────────────────────────
#  عروض الأسعار
# ──────────────────────────────────────

class Quotation(models.Model):
    STATUS_CHOICES = [
        ('draft',    'مسودة'),
        ('sent',     'مُرسل'),
        ('accepted', 'مقبول'),
        ('rejected', 'مرفوض'),
        ('expired',  'منتهي'),
    ]

    quote_number        = models.CharField(max_length=50, unique=True, editable=False)
    issue_date          = models.DateField(default=date.today)
    valid_until         = models.DateField(blank=True, null=True)
    client              = models.ForeignKey('clients.Client', on_delete=models.PROTECT, related_name='quotations')
    project             = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='quotations')
    status              = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    subtotal            = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount_amount     = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    vat_rate            = models.DecimalField(max_digits=5,  decimal_places=2, default=15)
    vat_amount          = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_amount        = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    notes               = models.TextField(blank=True)
    converted_to_invoice = models.OneToOneField(
        Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='from_quotation'
    )
    created_by          = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at          = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.quote_number

    def recalculate(self):
        from decimal import Decimal
        self.subtotal     = sum(l.total for l in self.lines.all())
        net               = self.subtotal - self.discount_amount
        self.vat_amount   = (net * self.vat_rate / Decimal('100')).quantize(Decimal('0.01'))
        self.total_amount = (net + self.vat_amount).quantize(Decimal('0.01'))
        self.save()

    def save(self, *args, **kwargs):
        if not self.quote_number:
            last = Quotation.objects.order_by('-id').first()
            n    = (last.id + 1) if last else 1
            self.quote_number = f'QUO-{n:05d}'
        super().save(*args, **kwargs)


class QuotationLine(models.Model):
    quotation   = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='lines')
    description = models.CharField(max_length=500)
    qty         = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit        = models.CharField(max_length=50, blank=True)
    unit_price  = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total       = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.total = self.qty * self.unit_price
        super().save(*args, **kwargs)


class InvoiceNote(models.Model):
    TYPE_CHOICES = [
        ('credit', 'إشعار دائن'),
        ('debit',  'إشعار مدين'),
        ('refund', 'استرجاع'),
    ]
    invoice     = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='invoice_notes')
    note_type   = models.CharField(max_length=10, choices=TYPE_CHOICES)
    note_number = models.CharField(max_length=50, unique=True, editable=False)
    amount      = models.DecimalField(max_digits=14, decimal_places=2)
    reason      = models.TextField(blank=True)
    date        = models.DateField(default=date.today)
    created_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def save(self, *args, **kwargs):
        if not self.note_number:
            prefix = {'credit': 'CRN', 'debit': 'DBN', 'refund': 'REF'}.get(self.note_type, 'NOTE')
            last = InvoiceNote.objects.order_by('-id').first()
            n = (last.id + 1) if last else 1
            self.note_number = f'{prefix}-{n:05d}'
        super().save(*args, **kwargs)
