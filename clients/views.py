from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from bconstproject.validators import validate_uploaded_image
from .models import Client

PAGE_SIZE = 8

@login_required
def client_list(request):
    q = request.GET.get('q', '').strip()
    client_type = request.GET.get('type', '')
    page_num = request.GET.get('page', 1)

    clients = Client.objects.all()
    if q:
        clients = clients.filter(name__icontains=q)
    if client_type in ('individual', 'company'):
        clients = clients.filter(client_type=client_type)

    paginator = Paginator(clients, PAGE_SIZE)
    page = paginator.get_page(page_num)

    total = Client.objects.count()
    individuals = Client.objects.filter(client_type='individual').count()
    companies = Client.objects.filter(client_type='company').count()

    return render(request, 'clients/client_list.html', {
        'clients': page,
        'page': page,
        'q': q,
        'type_filter': client_type,
        'total': total,
        'individuals': individuals,
        'companies': companies,
    })


@login_required
@require_http_methods(['POST'])
def client_create(request):
    try:
        data = request.POST
        logo = request.FILES.get('company_logo')
        if logo:
            error = validate_uploaded_image(logo)
            if error:
                return JsonResponse({'ok': False, 'error': error}, status=400)
        client = Client(
            client_type=data.get('client_type', 'individual'),
            name=data.get('name', '').strip(),
            phone=data.get('phone', '').strip(),
            email=data.get('email', '').strip(),
            address=data.get('address', '').strip(),
            notes=data.get('notes', '').strip(),
            national_id=data.get('national_id', '').strip(),
            tax_number=data.get('tax_number', '').strip(),
            commercial_registration=data.get('commercial_registration', '').strip(),
            contact_person=data.get('contact_person', '').strip(),
            contact_person_title=data.get('contact_person_title', '').strip(),
            website=data.get('website', '').strip(),
        )
        if logo:
            client.company_logo = logo
        client.save()
        return JsonResponse({'ok': True, 'id': client.id})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@login_required
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    data = {
        'id': client.id,
        'client_type': client.client_type,
        'name': client.name,
        'phone': client.phone,
        'email': client.email,
        'address': client.address,
        'notes': client.notes,
        'national_id': client.national_id,
        'tax_number': client.tax_number,
        'commercial_registration': client.commercial_registration,
        'contact_person': client.contact_person,
        'contact_person_title': client.contact_person_title,
        'website': client.website,
        'logo_url': client.company_logo.url if client.company_logo else '',
    }
    return JsonResponse(data)


@login_required
@require_http_methods(['POST'])
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)
    try:
        data = request.POST
        logo = request.FILES.get('company_logo')
        if logo:
            error = validate_uploaded_image(logo)
            if error:
                return JsonResponse({'ok': False, 'error': error}, status=400)
        client.client_type = data.get('client_type', client.client_type)
        client.name = data.get('name', client.name).strip()
        client.phone = data.get('phone', '').strip()
        client.email = data.get('email', '').strip()
        client.address = data.get('address', '').strip()
        client.notes = data.get('notes', '').strip()
        client.national_id = data.get('national_id', '').strip()
        client.tax_number = data.get('tax_number', '').strip()
        client.commercial_registration = data.get('commercial_registration', '').strip()
        client.contact_person = data.get('contact_person', '').strip()
        client.contact_person_title = data.get('contact_person_title', '').strip()
        client.website = data.get('website', '').strip()
        if logo:
            client.company_logo = logo
        elif data.get('remove_logo') == '1' and client.company_logo:
            client.company_logo.delete(save=False)
            client.company_logo = None
        client.save()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(['POST'])
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    try:
        if client.company_logo:
            client.company_logo.delete(save=False)
        client.delete()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)
