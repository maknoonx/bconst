from django.contrib import admin
from .models import Invoice, InvoiceLine, PaymentReceipt

class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 0

class PaymentReceiptInline(admin.TabularInline):
    model = PaymentReceipt
    extra = 0

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'client', 'status', 'total_amount', 'paid_amount', 'issue_date']
    list_filter = ['status']
    search_fields = ['invoice_number', 'client__name']
    inlines = [InvoiceLineInline, PaymentReceiptInline]

@admin.register(PaymentReceipt)
class PaymentReceiptAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'invoice', 'amount', 'payment_method', 'payment_date']
    list_filter = ['payment_method']
