import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Form, FormCategory, Letter, LetterCategory
from employees.models import Employee

LOGIN_URL = '/system/'


# ─── HOME (tabs: forms + letters) ────────────────────────────────────────────
@login_required(login_url=LOGIN_URL)
def namadhj_home(request):
    forms        = Form.objects.select_related('category').all()
    letters      = Letter.objects.select_related('category').all()
    form_cats    = FormCategory.objects.all()
    letter_cats  = LetterCategory.objects.all()

    q    = request.GET.get('q', '')
    cat  = request.GET.get('cat', '')
    tab  = request.GET.get('tab', 'forms')

    if q and tab == 'forms':
        forms = forms.filter(title__icontains=q)
    if cat and tab == 'forms':
        forms = forms.filter(category_id=cat)
    if q and tab == 'letters':
        letters = letters.filter(title__icontains=q)
    if cat and tab == 'letters':
        letters = letters.filter(category_id=cat)

    employees = Employee.objects.filter(status='A').order_by('first_name', 'last_name')

    return render(request, 'namadhj/namadhj.html', {
        'forms':       forms,
        'letters':     letters,
        'form_cats':   form_cats,
        'letter_cats': letter_cats,
        'employees':   employees,
        'q':           q,
        'cat':         cat,
        'tab':         tab,
    })


# ─── PRINT VIEWS ─────────────────────────────────────────────────────────────
@login_required(login_url=LOGIN_URL)
def form_print(request, pk):
    obj = get_object_or_404(Form, pk=pk)
    return render(request, 'namadhj/print_form.html', {'obj': obj})


@login_required(login_url=LOGIN_URL)
def letter_print(request, pk):
    obj = get_object_or_404(Letter, pk=pk)
    return render(request, 'namadhj/print_letter.html', {'obj': obj})


# ─── FORM CRUD (JSON API) ─────────────────────────────────────────────────────
@login_required(login_url=LOGIN_URL)
@require_POST
def form_create(request):
    try:
        d = json.loads(request.body)
        obj = Form.objects.create(
            title=d.get('title', ''),
            content=d.get('content', ''),
            footer_name=d.get('footer_name', '') or None,
            date=d.get('date') or None,
            category_id=d.get('category_id') or None,
        )
        return JsonResponse({'ok': True, 'pk': obj.pk})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@login_required(login_url=LOGIN_URL)
@require_POST
def form_edit(request, pk):
    try:
        obj = get_object_or_404(Form, pk=pk)
        d   = json.loads(request.body)
        obj.title       = d.get('title', obj.title)
        obj.content     = d.get('content', obj.content)
        obj.footer_name = d.get('footer_name', '') or None
        obj.date        = d.get('date') or obj.date
        obj.category_id = d.get('category_id') or None
        obj.save()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@login_required(login_url=LOGIN_URL)
@require_POST
def form_delete(request, pk):
    try:
        get_object_or_404(Form, pk=pk).delete()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@login_required(login_url=LOGIN_URL)
def form_detail_json(request, pk):
    obj = get_object_or_404(Form, pk=pk)
    return JsonResponse({
        'pk': obj.pk,
        'title': obj.title,
        'content': obj.content,
        'footer_name': obj.footer_name or '',
        'date': str(obj.date),
        'category_id': obj.category_id or '',
    })


# ─── LETTER CRUD (JSON API) ────────────────────────────────────────────────────
@login_required(login_url=LOGIN_URL)
@require_POST
def letter_create(request):
    try:
        d = json.loads(request.body)
        obj = Letter.objects.create(
            letter_number=d.get('letter_number', ''),
            title=d.get('title', ''),
            recipient=d.get('recipient', '') or None,
            subject=d.get('subject', '') or None,
            content=d.get('content', ''),
            footer_name=d.get('footer_name', '') or None,
            date=d.get('date') or None,
            category_id=d.get('category_id') or None,
        )
        return JsonResponse({'ok': True, 'pk': obj.pk})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@login_required(login_url=LOGIN_URL)
@require_POST
def letter_edit(request, pk):
    try:
        obj = get_object_or_404(Letter, pk=pk)
        d   = json.loads(request.body)
        obj.letter_number = d.get('letter_number', obj.letter_number)
        obj.title         = d.get('title', obj.title)
        obj.recipient     = d.get('recipient', '') or None
        obj.subject       = d.get('subject', '') or None
        obj.content       = d.get('content', obj.content)
        obj.footer_name   = d.get('footer_name', '') or None
        obj.date          = d.get('date') or obj.date
        obj.category_id   = d.get('category_id') or None
        obj.save()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@login_required(login_url=LOGIN_URL)
@require_POST
def letter_delete(request, pk):
    try:
        get_object_or_404(Letter, pk=pk).delete()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@login_required(login_url=LOGIN_URL)
def letter_detail_json(request, pk):
    obj = get_object_or_404(Letter, pk=pk)
    return JsonResponse({
        'pk': obj.pk,
        'letter_number': obj.letter_number,
        'title': obj.title,
        'recipient': obj.recipient or '',
        'subject': obj.subject or '',
        'content': obj.content,
        'footer_name': obj.footer_name or '',
        'date': str(obj.date),
        'category_id': obj.category_id or '',
    })


# ─── EMPLOYEE LETTERS ────────────────────────────────────────────────────────
EMP_LETTER_TYPES = {
    'salary':       'تعريف بالراتب',
    'employment':   'إثبات عمل',
    'experience':   'خطاب خبرة',
    'vacation':     'إذن إجازة',
    'end_service':  'إنهاء خدمة',
    'tazkia':       'خطاب تزكية',
}

@login_required(login_url=LOGIN_URL)
def emp_letter_print(request, letter_type, emp_pk):
    emp = get_object_or_404(Employee, pk=emp_pk)
    if letter_type not in EMP_LETTER_TYPES:
        from django.http import Http404
        raise Http404
    extra = {k: v for k, v in request.GET.items()}
    return render(request, 'namadhj/print_emp_letter.html', {
        'emp': emp,
        'letter_type': letter_type,
        'letter_title': EMP_LETTER_TYPES[letter_type],
        'extra': extra,
    })


@login_required(login_url=LOGIN_URL)
def emp_detail_json(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    return JsonResponse({
        'pk': emp.pk,
        'name': str(emp),
        'job_title': emp.job_title or '',
        'nationality': emp.nationality or '',
        'id_type': emp.get_id_type_display(),
        'id_number': emp.id_number or '',
        'employment_date': str(emp.employment_date) if emp.employment_date else '',
        'phone_number': emp.phone_number or '',
        'email': emp.email or '',
        'address': emp.address or '',
        'gender': emp.get_gender_display(),
    })


# ─── CATEGORY CRUD ────────────────────────────────────────────────────────────
@login_required(login_url=LOGIN_URL)
def form_cats_list(request):
    cats = list(FormCategory.objects.values('id', 'name').order_by('name'))
    return JsonResponse({'cats': cats})

@login_required(login_url=LOGIN_URL)
@require_POST
def form_cat_create(request):
    try:
        d = json.loads(request.body)
        obj = FormCategory.objects.create(name=d.get('name', ''))
        return JsonResponse({'ok': True, 'pk': obj.pk, 'name': obj.name})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})

@login_required(login_url=LOGIN_URL)
@require_POST
def form_cat_edit(request, pk):
    try:
        obj = get_object_or_404(FormCategory, pk=pk)
        d = json.loads(request.body)
        obj.name = d.get('name', obj.name)
        obj.save()
        return JsonResponse({'ok': True, 'name': obj.name})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})

@login_required(login_url=LOGIN_URL)
@require_POST
def form_cat_delete(request, pk):
    try:
        get_object_or_404(FormCategory, pk=pk).delete()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@login_required(login_url=LOGIN_URL)
def letter_cats_list(request):
    cats = list(LetterCategory.objects.values('id', 'name').order_by('name'))
    return JsonResponse({'cats': cats})

@login_required(login_url=LOGIN_URL)
@require_POST
def letter_cat_create(request):
    try:
        d = json.loads(request.body)
        obj = LetterCategory.objects.create(name=d.get('name', ''))
        return JsonResponse({'ok': True, 'pk': obj.pk, 'name': obj.name})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})

@login_required(login_url=LOGIN_URL)
@require_POST
def letter_cat_edit(request, pk):
    try:
        obj = get_object_or_404(LetterCategory, pk=pk)
        d = json.loads(request.body)
        obj.name = d.get('name', obj.name)
        obj.save()
        return JsonResponse({'ok': True, 'name': obj.name})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})

@login_required(login_url=LOGIN_URL)
@require_POST
def letter_cat_delete(request, pk):
    try:
        get_object_or_404(LetterCategory, pk=pk).delete()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})
