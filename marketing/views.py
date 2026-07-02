import json
from datetime import date

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import MonthlyPlan, PlanObjective, PlanBudget, PlanChannel, PlanChannelDay, PlanTarget, ExternalMarketer


def _parse_month(s):
    try:
        year, month = s.split('-')
        return date(int(year), int(month), 1)
    except Exception:
        return None


def _save_plan_relations(plan, objectives, budgets, channels, targets):
    plan.objectives.all().delete()
    plan.budgets.all().delete()
    plan.channels.all().delete()
    plan.targets.all().delete()

    for i, o in enumerate(objectives):
        PlanObjective.objects.create(plan=plan, title=o.get('title', ''), goal=o.get('goal', ''), order=i)

    for i, b in enumerate(budgets):
        try:
            amount = float(b.get('amount', 0) or 0)
        except (ValueError, TypeError):
            amount = 0
        PlanBudget.objects.create(plan=plan, budget_type=b.get('type', ''), amount=amount, order=i)

    for i, ch in enumerate(channels):
        channel = PlanChannel.objects.create(plan=plan, name=ch.get('name', ''), order=i)
        for day in ch.get('days', []):
            try:
                PlanChannelDay.objects.create(
                    channel=channel,
                    day_date=date.fromisoformat(day.get('date', '')),
                    content=day.get('content', ''),
                )
            except Exception:
                pass

    for i, t in enumerate(targets):
        try:
            tv = float(t.get('target_value', 0) or 0)
        except (ValueError, TypeError):
            tv = 0
        PlanTarget.objects.create(
            plan=plan,
            target_type=t.get('target_type', 'general'),
            label=t.get('label', ''),
            target_value=tv,
            order=i,
        )


@login_required(login_url='/system/')
def marketing_home(request):
    plans     = list(MonthlyPlan.objects.prefetch_related('objectives', 'budgets', 'channels__days', 'targets'))
    marketers = ExternalMarketer.objects.all()

    plans_data = []
    for p in plans:
        plans_data.append({
            'pk':           p.pk,
            'title':        p.title,
            'month':        p.month.strftime('%Y/%m'),
            'month_raw':    p.month.strftime('%Y-%m'),
            'status':       p.status,
            'status_label': p.get_status_display(),
            'notes':        p.notes,
            'total_budget': float(p.total_budget),
            'objectives': [{'title': o.title, 'goal': o.goal, 'result': o.result} for o in p.objectives.all()],
            'budgets':    [{'type': b.budget_type, 'amount': float(b.amount)} for b in p.budgets.all()],
            'channels':   [
                {'name': ch.name, 'days': [{'date': str(d.day_date), 'content': d.content} for d in ch.days.all()]}
                for ch in p.channels.all()
            ],
            'targets': [
                {
                    'target_type':  t.target_type,
                    'label':        t.label,
                    'target_value': float(t.target_value),
                    'result_value': float(t.result_value) if t.result_value is not None else None,
                }
                for t in p.targets.all()
            ],
        })

    context = {
        'plans_json':      json.dumps(plans_data, ensure_ascii=False),
        'plans':           plans,
        'marketers':       marketers,
        'total_plans':     len(plans),
        'active_plans':    sum(1 for p in plans if p.status == 'approved'),
        'done_plans':      sum(1 for p in plans if p.status == 'completed'),
        'total_marketers': marketers.filter(is_active=True).count(),
    }
    return render(request, 'marketing/marketing.html', context)


@login_required(login_url='/system/')
@require_POST
def plan_create(request):
    try:
        d = json.loads(request.body)
        month_date = _parse_month(d.get('month', ''))
        if not month_date:
            return JsonResponse({'ok': False, 'error': 'شهر غير صحيح'})
        plan = MonthlyPlan.objects.create(
            title=d.get('title', ''),
            month=month_date,
            notes=d.get('notes', ''),
            created_by=request.user,
        )
        _save_plan_relations(plan, d.get('objectives', []), d.get('budgets', []), d.get('channels', []), d.get('targets', []))
        return JsonResponse({'ok': True, 'pk': plan.pk})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@login_required(login_url='/system/')
@require_POST
def plan_edit(request, pk):
    try:
        plan = get_object_or_404(MonthlyPlan, pk=pk)
        d = json.loads(request.body)
        month_date = _parse_month(d.get('month', ''))
        if not month_date:
            return JsonResponse({'ok': False, 'error': 'شهر غير صحيح'})
        plan.title = d.get('title', plan.title)
        plan.month = month_date
        plan.notes = d.get('notes', plan.notes)
        plan.save()
        _save_plan_relations(plan, d.get('objectives', []), d.get('budgets', []), d.get('channels', []), d.get('targets', []))
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@login_required(login_url='/system/')
@require_POST
def plan_delete(request, pk):
    try:
        get_object_or_404(MonthlyPlan, pk=pk).delete()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@login_required(login_url='/system/')
@require_POST
def plan_approve(request, pk):
    try:
        plan = get_object_or_404(MonthlyPlan, pk=pk)
        plan.status = 'approved'
        plan.save()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@login_required(login_url='/system/')
@require_POST
def plan_complete(request, pk):
    try:
        plan = get_object_or_404(MonthlyPlan, pk=pk)
        plan.status = 'completed'
        plan.save()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@login_required(login_url='/system/')
@require_POST
def marketer_create(request):
    try:
        d = json.loads(request.body)
        ExternalMarketer.objects.create(
            name=d.get('name', ''),
            phone=d.get('phone', ''),
            email=d.get('email', ''),
            bank=d.get('bank', ''),
            iban=d.get('iban', ''),
            commission_rate=float(d.get('commission_rate', 0) or 0),
            settlement_schedule=d.get('settlement_schedule', 'monthly'),
            notes=d.get('notes', ''),
        )
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@login_required(login_url='/system/')
@require_POST
def marketer_edit(request, pk):
    try:
        m = get_object_or_404(ExternalMarketer, pk=pk)
        d = json.loads(request.body)
        m.name                = d.get('name', m.name)
        m.phone               = d.get('phone', m.phone)
        m.email               = d.get('email', m.email)
        m.bank                = d.get('bank', m.bank)
        m.iban                = d.get('iban', m.iban)
        m.commission_rate     = float(d.get('commission_rate', m.commission_rate) or 0)
        m.settlement_schedule = d.get('settlement_schedule', m.settlement_schedule)
        m.is_active           = d.get('is_active', m.is_active)
        m.notes               = d.get('notes', m.notes)
        m.save()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})


@login_required(login_url='/system/')
@require_POST
def marketer_delete(request, pk):
    try:
        get_object_or_404(ExternalMarketer, pk=pk).delete()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})

