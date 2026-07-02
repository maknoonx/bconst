import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from bconstproject.validators import validate_uploaded_image, validate_uploaded_file
from .models import CompanySettings, CompanyDocument, PaymentMethod


@login_required(login_url='/system/')
def company_home(request):
    company   = CompanySettings.objects.first()
    documents = CompanyDocument.objects.all()
    today     = timezone.now().date()
    expiring  = [d for d in documents if d.end_date and d.end_date <= today + timedelta(days=30)]
    return render(request, 'company/company.html', {
        'company':          company,
        'documents':        documents,
        'expiring':         expiring,
        'doc_type_choices': CompanyDocument.TYPE_CHOICES,
        'payment_methods':  PaymentMethod.objects.all(),
        'pm_type_choices':  PaymentMethod.TYPE_CHOICES,
    })


@login_required(login_url='/system/')
def company_save(request):
    if request.method != 'POST':
        return redirect('company_home')
    company = CompanySettings.objects.first()
    if not company:
        company = CompanySettings()
    fields = [
        'company_name_ar', 'company_name_en', 'unified_number', 'cr_number', 'cr_issue_date',
        'municipality_license', 'tax_registration_number', 'facility_address',
        'address_building_number', 'address_street', 'address_district', 'address_city', 'address_postal_code',
        'manager_name', 'manager_nationality', 'manager_id', 'manager_mobile', 'manager_email',
        'pr_mobile', 'pr_email', 'marketing_mobile', 'marketing_email', 'hr_email',
        'instagram', 'tiktok', 'facebook', 'youtube', 'twitter', 'snapchat',
        'google_maps_link', 'website_link',
    ]
    for f in fields:
        val = request.POST.get(f, '')
        setattr(company, f, val)
    if 'company_logo' in request.FILES:
        logo = request.FILES['company_logo']
        if not validate_uploaded_image(logo):
            company.company_logo = logo
    company.save()
    return redirect('company_home')


@login_required(login_url='/system/')
def doc_create(request):
    if request.method != 'POST':
        return redirect('company_home')
    d = CompanyDocument(
        file_type=request.POST.get('file_type', 'document'),
        file_name=request.POST.get('file_name', ''),
        notes=request.POST.get('notes', ''),
    )
    start = request.POST.get('start_date', '')
    end   = request.POST.get('end_date', '')
    if start:
        d.start_date = start
    if end:
        d.end_date = end
    if 'file' in request.FILES:
        f = request.FILES['file']
        if not validate_uploaded_file(f):
            d.file = f
    d.save()
    return redirect('company_home')


@login_required(login_url='/system/')
@require_POST
def doc_delete(request, pk):
    get_object_or_404(CompanyDocument, pk=pk).delete()
    return JsonResponse({'ok': True})


# ── طرق الدفع ──

@login_required(login_url='/system/')
@require_POST
def pm_create(request):
    data = json.loads(request.body)
    pm = PaymentMethod(
        name=data.get('name', '').strip(),
        payment_type=data.get('payment_type', 'immediate'),
        company_name=data.get('company_name', '').strip(),
        fee_percentage=data.get('fee_percentage') or 0,
        fixed_fee=data.get('fixed_fee') or 0,
        notes=data.get('notes', '').strip(),
        is_active=data.get('is_active', True),
    )
    pm.save()
    return JsonResponse({'ok': True, 'pk': pm.pk})


@login_required(login_url='/system/')
@require_POST
def pm_edit(request, pk):
    pm   = get_object_or_404(PaymentMethod, pk=pk)
    data = json.loads(request.body)
    pm.name           = data.get('name', '').strip()
    pm.payment_type   = data.get('payment_type', pm.payment_type)
    pm.company_name   = data.get('company_name', '').strip()
    pm.fee_percentage = data.get('fee_percentage') or 0
    pm.fixed_fee      = data.get('fixed_fee') or 0
    pm.notes          = data.get('notes', '').strip()
    pm.is_active      = data.get('is_active', pm.is_active)
    pm.save()
    return JsonResponse({'ok': True})


@login_required(login_url='/system/')
@require_POST
def pm_delete(request, pk):
    get_object_or_404(PaymentMethod, pk=pk).delete()
    return JsonResponse({'ok': True})
