import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum

from .models import (
    Warehouse, ItemCategory, Item, Supplier,
    PurchaseOrder, PurchaseOrderLine, StockMovement, Alert,
)

LOGIN_URL = '/system/'


def _err(msg, status=400):
    return JsonResponse({'ok': False, 'error': msg}, status=status)


# ── Main page ───────────────────────────────────────────────────
@login_required(login_url=LOGIN_URL)
def inventory_home(request):
    items     = Item.objects.select_related('warehouse', 'category').order_by('warehouse', 'name')
    orders    = PurchaseOrder.objects.select_related('supplier').prefetch_related('lines__item').order_by('-order_date')[:50]
    movements = StockMovement.objects.select_related('item', 'performed_by').order_by('-moved_at')[:100]
    alerts    = Alert.objects.select_related('item').filter(status='active')

    stats = {
        'total_items':      items.count(),
        'total_warehouses': Warehouse.objects.count(),
        'active_alerts':    alerts.count(),
        'pending_orders':   PurchaseOrder.objects.filter(status='pending').count(),
    }

    context = {
        'warehouses': Warehouse.objects.all(),
        'item_cats':  ItemCategory.objects.all(),
        'items':      items,
        'suppliers':  Supplier.objects.all(),
        'orders':     orders,
        'movements':  movements,
        'alerts':     alerts,
        'stats':      stats,
    }
    return render(request, 'inventory/inventory.html', context)


# ── Warehouses ──────────────────────────────────────────────────
@login_required(login_url=LOGIN_URL)
@require_POST
def warehouse_create(request):
    d = json.loads(request.body)
    name = d.get('name', '').strip()
    if not name:
        return _err('اسم المستودع مطلوب')
    wh = Warehouse.objects.create(name=name, location=d.get('location', '').strip(), notes=d.get('notes', '').strip())
    return JsonResponse({'ok': True, 'id': wh.id, 'name': wh.name})


@login_required(login_url=LOGIN_URL)
@require_POST
def warehouse_edit(request, pk):
    wh = get_object_or_404(Warehouse, pk=pk)
    d  = json.loads(request.body)
    name = d.get('name', '').strip()
    if not name:
        return _err('اسم المستودع مطلوب')
    wh.name = name; wh.location = d.get('location', '').strip(); wh.notes = d.get('notes', '').strip()
    wh.save()
    return JsonResponse({'ok': True})


@login_required(login_url=LOGIN_URL)
@require_POST
def warehouse_delete(request, pk):
    wh = get_object_or_404(Warehouse, pk=pk)
    if wh.items.exists():
        return _err('لا يمكن حذف مستودع يحتوي على أصناف')
    wh.delete()
    return JsonResponse({'ok': True})


# ── Item Categories ─────────────────────────────────────────────
@login_required(login_url=LOGIN_URL)
@require_POST
def item_cat_create(request):
    d = json.loads(request.body)
    name = d.get('name', '').strip()
    if not name:
        return _err('الاسم مطلوب')
    cat = ItemCategory.objects.create(name=name, type=d.get('type', 'other'))
    return JsonResponse({'ok': True, 'id': cat.id, 'name': cat.name})


@login_required(login_url=LOGIN_URL)
@require_POST
def item_cat_delete(request, pk):
    cat = get_object_or_404(ItemCategory, pk=pk)
    cat.delete()
    return JsonResponse({'ok': True})


# ── Items ───────────────────────────────────────────────────────
@login_required(login_url=LOGIN_URL)
@require_POST
def item_create(request):
    d = json.loads(request.body)
    name = d.get('name', '').strip()
    if not name:
        return _err('اسم الصنف مطلوب')
    if not d.get('warehouse_id'):
        return _err('المستودع مطلوب')
    item = Item.objects.create(
        warehouse_id=d['warehouse_id'],
        category_id=d.get('category_id') or None,
        name=name,
        sku=d.get('sku', '').strip() or None,
        unit=d.get('unit', '').strip(),
        qty_on_hand=d.get('qty_on_hand', 0),
        reorder_level=d.get('reorder_level', 0),
        unit_cost=d.get('unit_cost', 0),
        expiry_date=d.get('expiry_date') or None,
        notes=d.get('notes', '').strip(),
    )
    return JsonResponse({'ok': True, 'id': item.id})


@login_required(login_url=LOGIN_URL)
@require_POST
def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)
    d    = json.loads(request.body)
    name = d.get('name', '').strip()
    if not name:
        return _err('اسم الصنف مطلوب')
    item.warehouse_id  = d.get('warehouse_id', item.warehouse_id)
    item.category_id   = d.get('category_id') or None
    item.name          = name
    item.sku           = d.get('sku', '').strip() or None
    item.unit          = d.get('unit', '').strip()
    item.qty_on_hand   = d.get('qty_on_hand', item.qty_on_hand)
    item.reorder_level = d.get('reorder_level', item.reorder_level)
    item.unit_cost     = d.get('unit_cost', item.unit_cost)
    item.expiry_date   = d.get('expiry_date') or None
    item.notes         = d.get('notes', '').strip()
    item.save()
    return JsonResponse({'ok': True})


@login_required(login_url=LOGIN_URL)
@require_POST
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    item.delete()
    return JsonResponse({'ok': True})


# ── Suppliers ───────────────────────────────────────────────────
@login_required(login_url=LOGIN_URL)
@require_POST
def supplier_create(request):
    d = json.loads(request.body)
    name = d.get('name', '').strip()
    if not name:
        return _err('اسم المورد مطلوب')
    sup = Supplier.objects.create(
        name=name,
        contact_name=d.get('contact_name', '').strip(),
        phone=d.get('phone', '').strip(),
        email=d.get('email', '').strip(),
        notes=d.get('notes', '').strip(),
    )
    return JsonResponse({'ok': True, 'id': sup.id})


@login_required(login_url=LOGIN_URL)
@require_POST
def supplier_edit(request, pk):
    sup  = get_object_or_404(Supplier, pk=pk)
    d    = json.loads(request.body)
    name = d.get('name', '').strip()
    if not name:
        return _err('اسم المورد مطلوب')
    sup.name = name; sup.contact_name = d.get('contact_name', '').strip()
    sup.phone = d.get('phone', '').strip(); sup.email = d.get('email', '').strip()
    sup.notes = d.get('notes', '').strip(); sup.save()
    return JsonResponse({'ok': True})


@login_required(login_url=LOGIN_URL)
@require_POST
def supplier_delete(request, pk):
    sup = get_object_or_404(Supplier, pk=pk)
    if sup.orders.exists():
        return _err('لا يمكن حذف مورد مرتبط بأوامر شراء')
    sup.delete()
    return JsonResponse({'ok': True})


# ── Purchase Orders ─────────────────────────────────────────────
@login_required(login_url=LOGIN_URL)
@require_POST
def po_create(request):
    d = json.loads(request.body)
    if not d.get('supplier_id'):
        return _err('المورد مطلوب')
    order = PurchaseOrder.objects.create(
        supplier_id=d['supplier_id'],
        expected_date=d.get('expected_date') or None,
        notes=d.get('notes', '').strip(),
        created_by=request.user,
    )
    total = 0
    for ld in d.get('lines', []):
        item_id = ld.get('item_id')
        qty     = float(ld.get('qty', 0))
        price   = float(ld.get('unit_price', 0))
        if item_id and qty > 0:
            PurchaseOrderLine.objects.create(order=order, item_id=item_id, qty_ordered=qty, unit_price=price)
            total += qty * price
    order.total_amount = total
    order.save(update_fields=['total_amount'])
    return JsonResponse({'ok': True, 'id': order.id, 'ref': str(order)})


@login_required(login_url=LOGIN_URL)
def po_detail_json(request, pk):
    order = get_object_or_404(
        PurchaseOrder.objects.select_related('supplier', 'created_by').prefetch_related('lines__item'),
        pk=pk,
    )
    lines = [{
        'id':           ln.id,
        'item_name':    ln.item.name,
        'unit':         ln.item.unit,
        'qty_ordered':  float(ln.qty_ordered),
        'qty_received': float(ln.qty_received),
        'unit_price':   float(ln.unit_price),
        'line_total':   float(ln.qty_ordered * ln.unit_price),
    } for ln in order.lines.all()]
    return JsonResponse({
        'ok': True,
        'ref': str(order), 'supplier': order.supplier.name,
        'status': order.get_status_display(), 'order_date': str(order.order_date),
        'expected_date': str(order.expected_date) if order.expected_date else '',
        'total_amount': float(order.total_amount), 'notes': order.notes,
        'lines': lines,
    })


@login_required(login_url=LOGIN_URL)
@require_POST
def po_receive(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    if order.status != 'pending':
        return _err('فقط الأوامر المعلقة يمكن استلامها')
    for ln in order.lines.select_related('item').all():
        remaining = ln.qty_ordered - ln.qty_received
        if remaining > 0:
            ln.qty_received = ln.qty_ordered
            ln.save(update_fields=['qty_received'])
            ln.item.qty_on_hand += remaining
            ln.item.save(update_fields=['qty_on_hand'])
            StockMovement.objects.create(item=ln.item, performed_by=request.user,
                                         move_type='in', qty=remaining,
                                         reason=f'استلام من {order}')
            Alert.objects.filter(item=ln.item, alert_type='low_stock', status='active').update(status='resolved')
    order.status = 'received'
    order.save(update_fields=['status'])
    return JsonResponse({'ok': True})


@login_required(login_url=LOGIN_URL)
@require_POST
def po_cancel(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    if order.status != 'pending':
        return _err('فقط الأوامر المعلقة يمكن إلغاؤها')
    order.status = 'cancelled'
    order.save(update_fields=['status'])
    return JsonResponse({'ok': True})


@login_required(login_url=LOGIN_URL)
@require_POST
def po_delete(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    if order.status == 'received':
        return _err('لا يمكن حذف أمر مستلم')
    order.delete()
    return JsonResponse({'ok': True})


# ── Stock Movements ─────────────────────────────────────────────
@login_required(login_url=LOGIN_URL)
@require_POST
def movement_create(request):
    d         = json.loads(request.body)
    item_id   = d.get('item_id')
    move_type = d.get('move_type')
    qty_raw   = float(d.get('qty', 0))
    if not item_id or not move_type or qty_raw <= 0:
        return _err('بيانات غير مكتملة')

    item = get_object_or_404(Item, pk=item_id)

    if move_type == 'out' and float(item.qty_on_hand) < qty_raw:
        return _err(f'الكمية المتاحة ({item.qty_on_hand}) أقل من المطلوب صرفه')

    qty = qty_raw if move_type == 'in' else -qty_raw if move_type == 'out' else qty_raw

    StockMovement.objects.create(
        item=item, performed_by=request.user,
        move_type=move_type, qty=qty,
        reason=d.get('reason', '').strip(),
        project=d.get('project', '').strip(),
    )

    if move_type == 'adjust':
        item.qty_on_hand = qty_raw
    else:
        item.qty_on_hand += qty
    item.save(update_fields=['qty_on_hand'])

    if item.qty_on_hand <= item.reorder_level:
        Alert.objects.get_or_create(item=item, alert_type='low_stock', status='active')

    return JsonResponse({'ok': True, 'new_qty': float(item.qty_on_hand)})


# ── Alerts ──────────────────────────────────────────────────────
@login_required(login_url=LOGIN_URL)
@require_POST
def alert_resolve(request, pk):
    alert = get_object_or_404(Alert, pk=pk)
    alert.status = 'resolved'
    alert.save(update_fields=['status'])
    return JsonResponse({'ok': True})
