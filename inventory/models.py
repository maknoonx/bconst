from django.db import models
from django.contrib.auth.models import User


class ItemCategory(models.Model):
    TYPE_CHOICES = [
        ('materials',  'مواد بناء'),
        ('tools',      'أدوات وعدد'),
        ('equipment',  'معدات'),
        ('consumable', 'مستهلكات'),
        ('safety',     'معدات السلامة'),
        ('other',      'أخرى'),
    ]
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "تصنيف المواد"
        verbose_name_plural = "تصنيفات المواد"


class Warehouse(models.Model):
    name     = models.CharField(max_length=100)
    location = models.CharField(max_length=200, blank=True)
    notes    = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "مستودع"
        verbose_name_plural = "المستودعات"


class Item(models.Model):
    warehouse     = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='items')
    category      = models.ForeignKey(ItemCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    name          = models.CharField(max_length=200)
    sku           = models.CharField(max_length=100, unique=True, blank=True, null=True)
    unit          = models.CharField(max_length=50)
    qty_on_hand   = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reorder_level = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit_cost     = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expiry_date   = models.DateField(null=True, blank=True)
    notes         = models.TextField(blank=True)

    def __str__(self):
        return self.name

    @property
    def total_value(self):
        return self.qty_on_hand * self.unit_cost

    @property
    def is_low_stock(self):
        return self.qty_on_hand <= self.reorder_level

    class Meta:
        verbose_name = "صنف"
        verbose_name_plural = "الأصناف"


class Supplier(models.Model):
    name         = models.CharField(max_length=200)
    contact_name = models.CharField(max_length=200, blank=True)
    phone        = models.CharField(max_length=20, blank=True)
    email        = models.EmailField(blank=True)
    notes        = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "مورد"
        verbose_name_plural = "الموردون"


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('pending',   'قيد الانتظار'),
        ('received',  'مستلم'),
        ('cancelled', 'ملغي'),
    ]
    supplier      = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='orders')
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    order_date    = models.DateField(auto_now_add=True)
    expected_date = models.DateField(null=True, blank=True)
    total_amount  = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    notes         = models.TextField(blank=True)
    created_by    = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_orders')

    def __str__(self):
        return f"PO-{self.pk:04d} | {self.supplier.name}"

    class Meta:
        verbose_name = "أمر شراء"
        verbose_name_plural = "أوامر الشراء"
        ordering = ['-order_date']


class PurchaseOrderLine(models.Model):
    order        = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='lines')
    item         = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='order_lines')
    qty_ordered  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    qty_received = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit_price   = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.item.name} × {self.qty_ordered}"

    class Meta:
        verbose_name = "بند أمر الشراء"
        verbose_name_plural = "بنود أوامر الشراء"


class StockMovement(models.Model):
    MOVE_TYPE_CHOICES = [
        ('in',     'استلام'),
        ('out',    'صرف'),
        ('adjust', 'تعديل'),
    ]
    item         = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='movements')
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_movements')
    move_type    = models.CharField(max_length=10, choices=MOVE_TYPE_CHOICES)
    qty          = models.DecimalField(max_digits=12, decimal_places=2)
    reason       = models.CharField(max_length=255, blank=True)
    project      = models.CharField(max_length=200, blank=True)
    moved_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_move_type_display()} — {self.item.name} ({self.qty})"

    class Meta:
        verbose_name = "حركة مخزون"
        verbose_name_plural = "حركات المخزون"
        ordering = ['-moved_at']


class Alert(models.Model):
    ALERT_TYPE_CHOICES = [
        ('low_stock',     'مخزون منخفض'),
        ('expiry_soon',   'قرب انتهاء الصلاحية'),
        ('order_pending', 'أمر شراء معلق'),
    ]
    STATUS_CHOICES = [
        ('active',   'نشط'),
        ('resolved', 'تم الحل'),
    ]
    item         = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='alerts')
    alert_type   = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    status       = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    triggered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_alert_type_display()} — {self.item.name}"

    class Meta:
        verbose_name = "تنبيه"
        verbose_name_plural = "التنبيهات"
        ordering = ['-triggered_at']
