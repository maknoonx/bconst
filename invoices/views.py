import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Sum, Q
from .models import Invoice, InvoiceLine, PaymentReceipt, Quotation, QuotationLine, Service, ServiceCategory, InvoiceNote


# ──────────────────────────────────────────────────────────────
#  قائمة الفواتير الرئيسية
# ──────────────────────────────────────────────────────────────

@login_required(login_url='/system/')
def invoices_home(request):
    return _invoices_home(request)


# ──────────────────────────────────────────────────────────────
#  إدارة الخدمات
# ──────────────────────────────────────────────────────────────

@login_required(login_url='/system/')
@require_POST
def service_create(request):
    data = json.loads(request.body)
    s = Service(
        name=data.get('name', '').strip(),
        description=data.get('description', '').strip(),
        unit=data.get('unit', '').strip(),
        default_price=data.get('default_price') or 0,
        category=data.get('category', '').strip(),
        is_active=data.get('is_active', True),
    )
    s.save()
    return JsonResponse({'ok': True, 'pk': s.pk})


@login_required(login_url='/system/')
@require_POST
def service_edit(request, pk):
    s    = get_object_or_404(Service, pk=pk)
    data = json.loads(request.body)
    s.name          = data.get('name', '').strip()
    s.description   = data.get('description', '').strip()
    s.unit          = data.get('unit', '').strip()
    s.default_price = data.get('default_price') or 0
    s.category      = data.get('category', '').strip()
    s.is_active     = data.get('is_active', True)
    s.save()
    return JsonResponse({'ok': True})


@login_required(login_url='/system/')
@require_POST
def service_delete(request, pk):
    get_object_or_404(Service, pk=pk).delete()
    return JsonResponse({'ok': True})


@login_required(login_url='/system/')
def category_list(request):
    cats = list(ServiceCategory.objects.values_list('name', flat=True))
    return JsonResponse(cats, safe=False)


@login_required(login_url='/system/')
@require_POST
def category_create(request):
    data = json.loads(request.body)
    name = data.get('name', '').strip()
    if not name:
        return JsonResponse({'ok': False, 'error': 'الاسم مطلوب'})
    cat, created = ServiceCategory.objects.get_or_create(name=name)
    return JsonResponse({'ok': True, 'name': cat.name, 'created': created})


@login_required(login_url='/system/')
@require_POST
def category_delete(request, name):
    ServiceCategory.objects.filter(name=name).delete()
    return JsonResponse({'ok': True})


@login_required(login_url='/system/')
def service_search(request):
    q  = request.GET.get('q', '').strip()
    qs = Service.objects.filter(is_active=True)
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(category__icontains=q) | Q(description__icontains=q))
    qs = qs[:20]
    data = [{'id': s.id, 'name': s.name, 'unit': s.unit,
              'default_price': float(s.default_price), 'category': s.category,
              'description': s.description} for s in qs]
    return JsonResponse(data, safe=False)


@login_required(login_url='/system/')
def _invoices_home(request):
    invoices = Invoice.objects.select_related('client', 'project').all()
    receipts = PaymentReceipt.objects.select_related('invoice', 'invoice__client').all()
    quotes   = Quotation.objects.select_related('client', 'project').all()
    services   = Service.objects.all()
    categories = ServiceCategory.objects.all()
    return render(request, 'invoices/invoices.html', {
        'invoices':         invoices,
        'receipts':         receipts,
        'quotes':           quotes,
        'services':         services,
        'categories':       categories,
        'total_invoices':   invoices.count(),
        'total_draft':      invoices.filter(status='draft').count(),
        'total_paid':       invoices.filter(status='fully_paid').count(),
        'total_amount_all': invoices.aggregate(s=Sum('total_amount'))['s'] or 0,
        'total_collected':  invoices.aggregate(s=Sum('paid_amount'))['s'] or 0,
        'total_quotes':     quotes.count(),
        'total_services':   services.count(),
    })


# ──────────────────────────────────────────────────────────────
#  إنشاء / تعديل فاتورة
# ──────────────────────────────────────────────────────────────

@login_required(login_url='/system/')
def invoice_create(request):
    from clients.models import Client
    from projects.models import Project
    if request.method == 'POST':
        data = json.loads(request.body)
        invoice = Invoice(
            client_id=data['client_id'],
            project_id=data.get('project_id') or None,
            issue_date=data.get('issue_date') or None,
            due_date=data.get('due_date') or None,
            discount_amount=data.get('discount_amount') or 0,
            vat_rate=data.get('vat_rate') or 15,
            notes=data.get('notes', ''),
            created_by=request.user,
        )
        invoice.save()
        for line_data in data.get('lines', []):
            InvoiceLine.objects.create(
                invoice=invoice,
                description=line_data['description'],
                qty=line_data.get('qty', 1),
                unit=line_data.get('unit', ''),
                unit_price=line_data.get('unit_price', 0),
            )
        invoice.recalculate()
        return JsonResponse({'ok': True, 'pk': invoice.pk})
    return render(request, 'invoices/invoice_form.html', {
        'clients':  Client.objects.all(),
        'projects': [],
    })


@login_required(login_url='/system/')
def invoice_edit(request, pk):
    from clients.models import Client
    from projects.models import Project
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        data = json.loads(request.body)
        invoice.client_id       = data['client_id']
        invoice.project_id      = data.get('project_id') or None
        invoice.issue_date      = data.get('issue_date') or None
        invoice.due_date        = data.get('due_date') or None
        invoice.discount_amount = data.get('discount_amount') or 0
        invoice.vat_rate        = data.get('vat_rate') or 15
        invoice.notes           = data.get('notes', '')
        invoice.save()
        invoice.lines.all().delete()
        for line_data in data.get('lines', []):
            InvoiceLine.objects.create(
                invoice=invoice,
                description=line_data['description'],
                qty=line_data.get('qty', 1),
                unit=line_data.get('unit', ''),
                unit_price=line_data.get('unit_price', 0),
            )
        invoice.recalculate()
        return JsonResponse({'ok': True, 'pk': invoice.pk})
    return render(request, 'invoices/invoice_form.html', {
        'invoice':  invoice,
        'clients':  Client.objects.all(),
        'projects': list(invoice.client.projects.all()) if invoice.client_id else [],
    })


# ──────────────────────────────────────────────────────────────
#  تفاصيل / طباعة الفاتورة
# ──────────────────────────────────────────────────────────────

@login_required(login_url='/system/')
def invoice_detail(request, pk):
    from company.models import CompanySettings
    invoice  = get_object_or_404(Invoice, pk=pk)
    return render(request, 'invoices/invoice_detail.html', {
        'invoice':  invoice,
        'lines':    invoice.lines.all(),
        'receipts': invoice.receipts.all(),
        'notes':    invoice.invoice_notes.all(),
        'company':  CompanySettings.objects.first(),
    })


def _zatca_qr(seller_name, vat_number, invoice_dt, total_with_vat, vat_amount):
    """Generate ZATCA Phase-1 TLV base64 string then return QR code as base64 PNG."""
    import struct, base64, io
    import qrcode

    def tlv(tag, value):
        v = value.encode('utf-8')
        return bytes([tag, len(v)]) + v

    tlv_data = (
        tlv(1, seller_name) +
        tlv(2, vat_number) +
        tlv(3, invoice_dt.strftime('%Y-%m-%dT%H:%M:%SZ')) +
        tlv(4, f'{total_with_vat:.2f}') +
        tlv(5, f'{vat_amount:.2f}')
    )
    qr_string = base64.b64encode(tlv_data).decode()

    img = qrcode.make(qr_string)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


@login_required(login_url='/system/')
def invoice_print(request, pk):
    from company.models import CompanySettings
    from datetime import datetime
    invoice = get_object_or_404(Invoice, pk=pk)
    company = CompanySettings.objects.first()

    # Build QR code
    qr_img = None
    try:
        seller  = (company.company_name_ar or '') if company else ''
        vat_num = (company.tax_registration_number or '') if company else ''
        inv_dt  = datetime.combine(invoice.issue_date, datetime.min.time())
        qr_img  = _zatca_qr(seller, vat_num, inv_dt,
                             invoice.total_amount, invoice.vat_amount)
    except Exception:
        pass

    # Logo as base64 so it renders in print
    logo_b64 = None
    try:
        if company and company.company_logo:
            import base64 as b64
            with open(company.company_logo.path, 'rb') as f:
                raw = f.read()
            ext = company.company_logo.name.rsplit('.', 1)[-1].lower()
            mime = 'image/png' if ext == 'png' else 'image/jpeg'
            logo_b64 = f'data:{mime};base64,' + b64.b64encode(raw).decode()
    except Exception:
        pass

    return render(request, 'invoices/invoice_print.html', {
        'invoice':  invoice,
        'lines':    invoice.lines.all(),
        'company':  company,
        'qr_img':   qr_img,
        'logo_b64': logo_b64,
    })


# ──────────────────────────────────────────────────────────────
#  إجراءات الفاتورة
# ──────────────────────────────────────────────────────────────

@login_required(login_url='/system/')
@require_POST
def invoice_finalize(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.status = 'final'
    invoice.save()
    return JsonResponse({'ok': True})


@login_required(login_url='/system/')
@require_POST
def invoice_cancel(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.status = 'cancelled'
    invoice.save()
    return JsonResponse({'ok': True})


@login_required(login_url='/system/')
@require_POST
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if invoice.status == 'draft':
        invoice.delete()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False, 'error': 'يمكن حذف المسودات فقط'})


# ──────────────────────────────────────────────────────────────
#  سندات القبض
# ──────────────────────────────────────────────────────────────

@login_required(login_url='/system/')
@require_POST
def payment_add(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    data    = json.loads(request.body)
    receipt = PaymentReceipt(
        invoice=invoice,
        amount=data['amount'],
        payment_method=data.get('payment_method', 'cash'),
        payment_date=data.get('payment_date'),
        notes=data.get('notes', ''),
        created_by=request.user,
    )
    receipt.save()
    return JsonResponse({'ok': True, 'receipt_pk': receipt.pk})


@login_required(login_url='/system/')
def receipt_print(request, pk):
    from company.models import CompanySettings
    receipt = get_object_or_404(PaymentReceipt, pk=pk)
    return render(request, 'invoices/receipt_print.html', {
        'receipt': receipt,
        'company': CompanySettings.objects.first(),
    })


@login_required(login_url='/system/')
@require_POST
def receipt_delete(request, pk):
    receipt = get_object_or_404(PaymentReceipt, pk=pk)
    invoice = receipt.invoice
    receipt.delete()
    invoice.recalculate()
    return JsonResponse({'ok': True})


# ──────────────────────────────────────────────────────────────
#  API: بحث
# ──────────────────────────────────────────────────────────────

@login_required(login_url='/system/')
def client_search(request):
    from clients.models import Client
    q       = request.GET.get('q', '')
    clients = Client.objects.filter(name__icontains=q)[:10]
    return JsonResponse([{'id': c.id, 'name': str(c)} for c in clients], safe=False)


@login_required(login_url='/system/')
def project_search(request):
    from projects.models import Project
    q = request.GET.get('q', '').strip()
    qs = Project.objects.all()
    if q:
        qs = qs.filter(name__icontains=q)
    client_id = request.GET.get('client_id')
    if client_id:
        qs = qs.filter(client_id=client_id)
    return JsonResponse([{'id': p.id, 'name': str(p)} for p in qs[:30]], safe=False)


@login_required(login_url='/system/')
def item_search(request):
    from inventory.models import Item
    q   = request.GET.get('q', '').strip()
    qs  = Item.objects.select_related('category')
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(sku__icontains=q))
    qs = qs[:15]
    data = [{
        'id':         item.id,
        'name':       item.name,
        'sku':        item.sku or '',
        'unit':       item.unit,
        'unit_cost':  float(item.unit_cost),
    } for item in qs]
    return JsonResponse(data, safe=False)


# ──────────────────────────────────────────────────────────────
#  عروض الأسعار
# ──────────────────────────────────────────────────────────────

@login_required(login_url='/system/')
def quotes_list(request):
    quotes = Quotation.objects.select_related('client', 'project').all()
    return render(request, 'invoices/quotes_list.html', {'quotes': quotes})


def _save_quote_data(quote, data):
    quote.client_id       = data['client_id']
    quote.project_id      = data.get('project_id') or None
    quote.issue_date      = data.get('issue_date') or None
    quote.valid_until     = data.get('valid_until') or None
    quote.discount_amount = data.get('discount_amount') or 0
    quote.vat_rate        = data.get('vat_rate') or 15
    quote.notes           = data.get('notes', '')
    quote.save()
    quote.lines.all().delete()
    for line_data in data.get('lines', []):
        QuotationLine.objects.create(
            quotation=quote,
            description=line_data['description'],
            qty=line_data.get('qty', 1),
            unit=line_data.get('unit', ''),
            unit_price=line_data.get('unit_price', 0),
        )
    quote.recalculate()


@login_required(login_url='/system/')
def quote_create(request):
    from clients.models import Client
    if request.method == 'POST':
        data  = json.loads(request.body)
        quote = Quotation(created_by=request.user)
        _save_quote_data(quote, data)
        return JsonResponse({'ok': True, 'pk': quote.pk})
    return render(request, 'invoices/quote_form.html', {'clients': Client.objects.all()})


@login_required(login_url='/system/')
def quote_edit(request, pk):
    from clients.models import Client
    quote = get_object_or_404(Quotation, pk=pk)
    if request.method == 'POST':
        data = json.loads(request.body)
        _save_quote_data(quote, data)
        return JsonResponse({'ok': True, 'pk': quote.pk})
    return render(request, 'invoices/quote_form.html', {
        'quote':    quote,
        'clients':  Client.objects.all(),
        'projects': list(quote.client.projects.all()) if quote.client_id else [],
    })


@login_required(login_url='/system/')
def quote_detail(request, pk):
    from company.models import CompanySettings
    quote = get_object_or_404(Quotation, pk=pk)
    return render(request, 'invoices/quote_detail.html', {
        'quote':   quote,
        'lines':   quote.lines.all(),
        'company': CompanySettings.objects.first(),
    })


@login_required(login_url='/system/')
def quote_print(request, pk):
    from company.models import CompanySettings
    quote   = get_object_or_404(Quotation, pk=pk)
    company = CompanySettings.objects.first()

    logo_b64 = None
    try:
        if company and company.company_logo:
            import base64 as b64
            with open(company.company_logo.path, 'rb') as f:
                raw = f.read()
            ext  = company.company_logo.name.rsplit('.', 1)[-1].lower()
            mime = 'image/png' if ext == 'png' else 'image/jpeg'
            logo_b64 = f'data:{mime};base64,' + b64.b64encode(raw).decode()
    except Exception:
        pass

    return render(request, 'invoices/quote_print.html', {
        'quote':    quote,
        'lines':    quote.lines.all(),
        'company':  company,
        'logo_b64': logo_b64,
    })


@login_required(login_url='/system/')
@require_POST
def quote_send(request, pk):
    quote = get_object_or_404(Quotation, pk=pk)
    quote.status = 'sent'
    quote.save()
    return JsonResponse({'ok': True})


@login_required(login_url='/system/')
@require_POST
def quote_accept(request, pk):
    quote = get_object_or_404(Quotation, pk=pk)
    quote.status = 'accepted'
    quote.save()
    return JsonResponse({'ok': True})


@login_required(login_url='/system/')
@require_POST
def quote_reject(request, pk):
    quote = get_object_or_404(Quotation, pk=pk)
    quote.status = 'rejected'
    quote.save()
    return JsonResponse({'ok': True})


@login_required(login_url='/system/')
@require_POST
def quote_convert(request, pk):
    quote = get_object_or_404(Quotation, pk=pk)
    if quote.converted_to_invoice:
        return JsonResponse({'ok': False, 'error': 'تم تحويله مسبقاً'})
    invoice = Invoice(
        client_id=quote.client_id,
        project_id=quote.project_id,
        issue_date=quote.issue_date,
        discount_amount=quote.discount_amount,
        vat_rate=quote.vat_rate,
        notes=quote.notes,
        created_by=request.user,
    )
    invoice.save()
    for ql in quote.lines.all():
        InvoiceLine.objects.create(
            invoice=invoice,
            description=ql.description,
            qty=ql.qty,
            unit=ql.unit,
            unit_price=ql.unit_price,
        )
    invoice.recalculate()
    quote.converted_to_invoice = invoice
    quote.status = 'accepted'
    quote.save()
    return JsonResponse({'ok': True, 'invoice_pk': invoice.pk})


@login_required(login_url='/system/')
@require_POST
def quote_delete(request, pk):
    quote = get_object_or_404(Quotation, pk=pk)
    if quote.status == 'draft':
        quote.delete()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False, 'error': 'يمكن حذف المسودات فقط'})


# ──────────────────────────────────────────────────────────────
#  تغيير العميل والإشعارات
# ──────────────────────────────────────────────────────────────

@login_required(login_url='/system/')
@require_POST
def invoice_change_client(request, pk):
    from clients.models import Client
    invoice = get_object_or_404(Invoice, pk=pk)
    data = json.loads(request.body)
    client_id = data.get('client_id')
    if not client_id:
        return JsonResponse({'ok': False, 'error': 'العميل مطلوب'})
    invoice.client_id = client_id
    invoice.project_id = data.get('project_id') or None
    invoice.save()
    return JsonResponse({'ok': True, 'client_name': invoice.client.name})


@login_required(login_url='/system/')
@require_POST
def invoice_note_add(request, pk):
    from decimal import Decimal
    invoice = get_object_or_404(Invoice, pk=pk)
    data = json.loads(request.body)
    note_type = data.get('note_type')
    amount = data.get('amount')

    if note_type not in ('credit', 'debit', 'refund'):
        return JsonResponse({'ok': False, 'error': 'نوع الإشعار غير صحيح'})
    if not amount or float(amount) <= 0:
        return JsonResponse({'ok': False, 'error': 'المبلغ يجب أن يكون أكبر من صفر'})

    amount_d = Decimal(str(amount))

    # ── شروط التحقق ──
    if note_type == 'refund':
        # الاسترجاع لا يمكن إضافته إلا إذا كان هناك مبلغ مسدّد
        if invoice.paid_amount <= 0:
            return JsonResponse({'ok': False, 'error': 'لا يمكن إضافة استرجاع لفاتورة لم يُسدَّد منها أي مبلغ'})
        # مبلغ الاسترجاع لا يتجاوز المبلغ المسدّد الفعلي (بعد خصم الاسترجاعات السابقة)
        effective_paid = invoice.paid_amount - invoice.refund_total
        if amount_d > effective_paid:
            return JsonResponse({'ok': False,
                'error': f'مبلغ الاسترجاع ({amount_d:.2f} ر.س) أكبر من المبلغ المسدّد الفعلي ({effective_paid:.2f} ر.س)'})

    if note_type == 'credit':
        # الإشعار الدائن لا يتجاوز إجمالي الفاتورة المعدّل الحالي
        if amount_d > invoice.adjusted_total:
            return JsonResponse({'ok': False,
                'error': f'الإشعار الدائن ({amount_d:.2f} ر.س) أكبر من إجمالي الفاتورة ({invoice.adjusted_total:.2f} ر.س)'})

    if note_type == 'debit':
        # لا قيود صارمة على الإشعار المدين لكن يجب أن يكون الإجمالي معقولاً
        if amount_d <= 0:
            return JsonResponse({'ok': False, 'error': 'مبلغ الإشعار المدين غير صحيح'})

    note = InvoiceNote(
        invoice=invoice,
        note_type=note_type,
        amount=amount,
        reason=data.get('reason', '').strip(),
        date=data.get('date') or None,
        created_by=request.user,
    )
    note.save()
    return JsonResponse({'ok': True, 'note_pk': note.pk, 'note_number': note.note_number})


@login_required(login_url='/system/')
@require_POST
def invoice_note_delete(request, note_pk):
    note = get_object_or_404(InvoiceNote, pk=note_pk)
    note.delete()
    return JsonResponse({'ok': True})


@login_required(login_url='/system/')
@require_POST
def receipt_edit(request, pk):
    from .models import PaymentReceipt
    receipt = get_object_or_404(PaymentReceipt, pk=pk)
    data = json.loads(request.body)
    method = data.get('payment_method', '').strip()
    valid_methods = {'cash', 'transfer', 'check', 'card', 'other'}
    if method not in valid_methods:
        return JsonResponse({'ok': False, 'error': 'طريقة دفع غير صحيحة'})
    receipt.payment_method = method
    receipt.notes = data.get('notes', '').strip()
    receipt.save()
    return JsonResponse({'ok': True})


@login_required(login_url='/system/')
def invoice_note_print(request, note_pk):
    note = get_object_or_404(InvoiceNote, pk=note_pk)
    return render(request, 'invoices/note_print.html', {'note': note})
