from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import (
    Account, AccountType, CostCenter,
    Journal, JournalLine,
    FixedAsset, AccountingPeriod,
    PayrollRun, PayrollLine,
)
from employees.models import Employee

LOGIN_URL = '/system/'


# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------

@login_required(login_url=LOGIN_URL)
def accounting_home(request):
    accounts          = Account.objects.select_related('account_type', 'parent').all()
    recent_journals   = Journal.objects.filter(is_posted=True).order_by('-date', '-id')[:10]
    cost_centers      = CostCenter.objects.all()
    fixed_assets      = FixedAsset.objects.select_related('cost_center').all()
    payroll_runs      = PayrollRun.objects.all()
    accounting_periods = AccountingPeriod.objects.all()
    employees         = Employee.objects.all()
    account_types     = AccountType.objects.all()

    stats = {
        'total_accounts':  accounts.count(),
        'total_journals':  Journal.objects.count(),
        'total_assets':    fixed_assets.count(),
        'total_payrolls':  payroll_runs.count(),
    }

    context = {
        'accounts':           accounts,
        'recent_journals':    recent_journals,
        'cost_centers':       cost_centers,
        'fixed_assets':       fixed_assets,
        'payroll_runs':       payroll_runs,
        'accounting_periods': accounting_periods,
        'employees':          employees,
        'account_types':      account_types,
        'stats':              stats,
    }
    return render(request, 'accounting/accounting.html', context)


# ---------------------------------------------------------------------------
# Accounts
# ---------------------------------------------------------------------------

@login_required(login_url=LOGIN_URL)
@require_POST
def account_create(request):
    try:
        account_type = get_object_or_404(AccountType, pk=request.POST.get('account_type'))
        parent_id    = request.POST.get('parent') or None
        parent       = get_object_or_404(Account, pk=parent_id) if parent_id else None

        account = Account.objects.create(
            code         = request.POST.get('code', '').strip(),
            name         = request.POST.get('name', '').strip(),
            account_type = account_type,
            parent       = parent,
            is_active    = request.POST.get('is_active', 'true') == 'true',
            notes        = request.POST.get('notes', '').strip(),
        )
        return JsonResponse({'ok': True, 'id': account.pk, 'code': account.code, 'name': account.name})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@login_required(login_url=LOGIN_URL)
def account_edit(request, pk):
    account = get_object_or_404(Account, pk=pk)

    if request.method == 'GET':
        return JsonResponse({
            'ok':           True,
            'id':           account.pk,
            'code':         account.code,
            'name':         account.name,
            'account_type': account.account_type_id,
            'parent':       account.parent_id,
            'is_active':    account.is_active,
            'notes':        account.notes,
        })

    if request.method == 'POST':
        try:
            account_type = get_object_or_404(AccountType, pk=request.POST.get('account_type'))
            parent_id    = request.POST.get('parent') or None
            parent       = get_object_or_404(Account, pk=parent_id) if parent_id else None

            account.code         = request.POST.get('code', account.code).strip()
            account.name         = request.POST.get('name', account.name).strip()
            account.account_type = account_type
            account.parent       = parent
            account.is_active    = request.POST.get('is_active', 'true') == 'true'
            account.notes        = request.POST.get('notes', account.notes).strip()
            account.save()
            return JsonResponse({'ok': True, 'id': account.pk})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)

    return JsonResponse({'ok': False, 'error': 'Method not allowed'}, status=405)


@login_required(login_url=LOGIN_URL)
@require_POST
def account_delete(request, pk):
    account = get_object_or_404(Account, pk=pk)
    try:
        account.delete()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


# ---------------------------------------------------------------------------
# Journals
# ---------------------------------------------------------------------------

@login_required(login_url=LOGIN_URL)
@require_POST
def journal_create(request):
    try:
        cost_center_id = request.POST.get('cost_center') or None
        cost_center    = get_object_or_404(CostCenter, pk=cost_center_id) if cost_center_id else None

        journal = Journal.objects.create(
            date        = request.POST.get('date'),
            description = request.POST.get('description', '').strip(),
            source_type = request.POST.get('source_type', 'manual'),
            cost_center = cost_center,
            created_by  = request.user,
        )

        account_ids = request.POST.getlist('line_account[]')
        debits      = request.POST.getlist('line_debit[]')
        credits     = request.POST.getlist('line_credit[]')
        notes       = request.POST.getlist('line_note[]')

        for i, acc_id in enumerate(account_ids):
            if not acc_id:
                continue
            account = get_object_or_404(Account, pk=acc_id)
            debit   = Decimal(debits[i] or '0')
            credit  = Decimal(credits[i] or '0')
            note    = notes[i] if i < len(notes) else ''
            JournalLine.objects.create(
                journal = journal,
                account = account,
                debit   = debit,
                credit  = credit,
                note    = note,
            )

        return JsonResponse({'ok': True, 'id': journal.pk, 'number': journal.number, 'balanced': journal.is_balanced()})
    except (InvalidOperation, ValueError) as e:
        return JsonResponse({'ok': False, 'error': f'خطأ في المبالغ: {e}'}, status=400)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@login_required(login_url=LOGIN_URL)
def journal_detail(request, pk):
    journal = get_object_or_404(Journal, pk=pk)
    lines   = []
    for line in journal.lines.select_related('account').all():
        lines.append({
            'id':      line.pk,
            'account': {'id': line.account_id, 'code': line.account.code, 'name': line.account.name},
            'debit':   str(line.debit),
            'credit':  str(line.credit),
            'note':    line.note,
        })

    data = {
        'ok':          True,
        'id':          journal.pk,
        'number':      journal.number,
        'date':        str(journal.date),
        'description': journal.description,
        'source_type': journal.source_type,
        'cost_center': journal.cost_center_id,
        'is_posted':   journal.is_posted,
        'total_debit': str(journal.get_total_debit()),
        'total_credit': str(journal.get_total_credit()),
        'balanced':    journal.is_balanced(),
        'lines':       lines,
    }
    return JsonResponse(data)


@login_required(login_url=LOGIN_URL)
@require_POST
def journal_post(request, pk):
    journal = get_object_or_404(Journal, pk=pk)
    try:
        journal.post()
        return JsonResponse({'ok': True, 'number': journal.number})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@login_required(login_url=LOGIN_URL)
@require_POST
def journal_delete(request, pk):
    journal = get_object_or_404(Journal, pk=pk)
    if journal.is_posted:
        return JsonResponse({'ok': False, 'error': 'لا يمكن حذف قيد معتمد.'}, status=400)
    try:
        journal.delete()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


# ---------------------------------------------------------------------------
# Fixed Assets
# ---------------------------------------------------------------------------

@login_required(login_url=LOGIN_URL)
@require_POST
def asset_create(request):
    try:
        cost_center_id = request.POST.get('cost_center') or None
        cost_center    = get_object_or_404(CostCenter, pk=cost_center_id) if cost_center_id else None

        asset = FixedAsset.objects.create(
            name               = request.POST.get('name', '').strip(),
            category           = request.POST.get('category', 'other'),
            purchase_date      = request.POST.get('purchase_date'),
            cost               = Decimal(request.POST.get('cost', '0')),
            useful_life_months = int(request.POST.get('useful_life_months', 1)),
            salvage_value      = Decimal(request.POST.get('salvage_value', '0')),
            cost_center        = cost_center,
            is_active          = request.POST.get('is_active', 'true') == 'true',
            notes              = request.POST.get('notes', '').strip(),
        )
        return JsonResponse({'ok': True, 'id': asset.pk, 'name': asset.name, 'monthly_depreciation': str(asset.monthly_depreciation())})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@login_required(login_url=LOGIN_URL)
def asset_edit(request, pk):
    asset = get_object_or_404(FixedAsset, pk=pk)

    if request.method == 'GET':
        return JsonResponse({
            'ok':                True,
            'id':                asset.pk,
            'name':              asset.name,
            'category':          asset.category,
            'purchase_date':     str(asset.purchase_date),
            'cost':              str(asset.cost),
            'useful_life_months': asset.useful_life_months,
            'salvage_value':     str(asset.salvage_value),
            'cost_center':       asset.cost_center_id,
            'is_active':         asset.is_active,
            'notes':             asset.notes,
            'monthly_depreciation': str(asset.monthly_depreciation()),
        })

    if request.method == 'POST':
        try:
            cost_center_id = request.POST.get('cost_center') or None
            cost_center    = get_object_or_404(CostCenter, pk=cost_center_id) if cost_center_id else None

            asset.name               = request.POST.get('name', asset.name).strip()
            asset.category           = request.POST.get('category', asset.category)
            asset.purchase_date      = request.POST.get('purchase_date', asset.purchase_date)
            asset.cost               = Decimal(request.POST.get('cost', str(asset.cost)))
            asset.useful_life_months = int(request.POST.get('useful_life_months', asset.useful_life_months))
            asset.salvage_value      = Decimal(request.POST.get('salvage_value', str(asset.salvage_value)))
            asset.cost_center        = cost_center
            asset.is_active          = request.POST.get('is_active', 'true') == 'true'
            asset.notes              = request.POST.get('notes', asset.notes).strip()
            asset.save()
            return JsonResponse({'ok': True, 'id': asset.pk})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)

    return JsonResponse({'ok': False, 'error': 'Method not allowed'}, status=405)


@login_required(login_url=LOGIN_URL)
@require_POST
def asset_delete(request, pk):
    asset = get_object_or_404(FixedAsset, pk=pk)
    try:
        asset.delete()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


# ---------------------------------------------------------------------------
# Payroll
# ---------------------------------------------------------------------------

@login_required(login_url=LOGIN_URL)
@require_POST
def payroll_create(request):
    try:
        year  = int(request.POST.get('year'))
        month = int(request.POST.get('month'))

        payroll = PayrollRun.objects.create(
            year       = year,
            month      = month,
            created_by = request.user,
            notes      = request.POST.get('notes', '').strip(),
        )

        employee_ids    = request.POST.getlist('employee_id[]')
        basics          = request.POST.getlist('basic[]')
        allowances_list = request.POST.getlist('allowances[]')
        deductions_list = request.POST.getlist('deductions[]')
        ded_notes       = request.POST.getlist('deduction_note[]')
        bonuses         = request.POST.getlist('bonus[]')
        bonus_notes     = request.POST.getlist('bonus_note[]')

        total_gross = Decimal('0')
        total_net   = Decimal('0')

        for i, emp_id in enumerate(employee_ids):
            if not emp_id:
                continue
            employee   = get_object_or_404(Employee, pk=emp_id)
            basic      = Decimal(basics[i] if i < len(basics) else '0')
            allowances = Decimal(allowances_list[i] if i < len(allowances_list) else '0')
            deductions = Decimal(deductions_list[i] if i < len(deductions_list) else '0')
            bonus      = Decimal(bonuses[i] if i < len(bonuses) else '0')

            line = PayrollLine.objects.create(
                payroll        = payroll,
                employee       = employee,
                basic          = basic,
                allowances     = allowances,
                deductions     = deductions,
                deduction_note = ded_notes[i] if i < len(ded_notes) else '',
                bonus          = bonus,
                bonus_note     = bonus_notes[i] if i < len(bonus_notes) else '',
            )
            total_gross += line.gross
            total_net   += line.net

        payroll.total_gross = total_gross
        payroll.total_net   = total_net
        payroll.save()

        return JsonResponse({'ok': True, 'id': payroll.pk, 'total_gross': str(total_gross), 'total_net': str(total_net)})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@login_required(login_url=LOGIN_URL)
def payroll_detail(request, pk):
    payroll = get_object_or_404(PayrollRun, pk=pk)
    lines   = []
    for line in payroll.lines.select_related('employee').all():
        lines.append({
            'id':             line.pk,
            'employee':       {'id': line.employee_id, 'name': str(line.employee)},
            'basic':          str(line.basic),
            'allowances':     str(line.allowances),
            'deductions':     str(line.deductions),
            'deduction_note': line.deduction_note,
            'bonus':          str(line.bonus),
            'bonus_note':     line.bonus_note,
            'gross':          str(line.gross),
            'net':            str(line.net),
        })

    data = {
        'ok':          True,
        'id':          payroll.pk,
        'year':        payroll.year,
        'month':       payroll.month,
        'status':      payroll.status,
        'total_gross': str(payroll.total_gross),
        'total_net':   str(payroll.total_net),
        'notes':       payroll.notes,
        'lines':       lines,
    }
    return JsonResponse(data)


@login_required(login_url=LOGIN_URL)
@require_POST
def payroll_post(request, pk):
    payroll = get_object_or_404(PayrollRun, pk=pk)
    try:
        total_gross = Decimal('0')
        total_net   = Decimal('0')
        for line in payroll.lines.all():
            total_gross += line.gross
            total_net   += line.net

        payroll.total_gross = total_gross
        payroll.total_net   = total_net
        payroll.status      = 'posted'
        payroll.save()
        return JsonResponse({'ok': True, 'id': payroll.pk, 'total_gross': str(total_gross), 'total_net': str(total_net)})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


# ---------------------------------------------------------------------------
# Accounting Periods
# ---------------------------------------------------------------------------

@login_required(login_url=LOGIN_URL)
@require_POST
def period_create(request):
    try:
        period = AccountingPeriod.objects.create(
            year  = int(request.POST.get('year')),
            month = int(request.POST.get('month')),
        )
        return JsonResponse({'ok': True, 'id': period.pk, 'label': str(period)})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@login_required(login_url=LOGIN_URL)
@require_POST
def period_toggle(request, pk):
    period = get_object_or_404(AccountingPeriod, pk=pk)
    try:
        if period.status == 'open':
            period.status    = 'closed'
            period.closed_by = request.user
            period.closed_at = timezone.now()
        else:
            period.status    = 'open'
            period.closed_by = None
            period.closed_at = None
        period.save()
        return JsonResponse({'ok': True, 'status': period.status, 'label': str(period)})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)
