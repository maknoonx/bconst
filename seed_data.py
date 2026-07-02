"""
Run:  python manage.py shell < seed_data.py
"""
import os, django, decimal
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bconstproject.settings')

from datetime import date
from decimal import Decimal as D
from django.contrib.auth.models import User

# ═══════════════════════════════════════════
# ACCOUNTING
# ═══════════════════════════════════════════
from accounting.models import (
    AccountType, Account, CostCenter, Journal, JournalLine,
    FixedAsset, AccountingPeriod, PayrollRun, PayrollLine,
)
from employees.models import Employee

# ── Account Types (keyed by category, which is unique) ──────────
normal = {'asset':'debit','liability':'credit','equity':'credit','revenue':'credit','expense':'debit'}
at_asset, _ = AccountType.objects.get_or_create(category='asset',     defaults={'normal_balance': normal['asset']})
at_liab,  _ = AccountType.objects.get_or_create(category='liability', defaults={'normal_balance': normal['liability']})
at_eq,    _ = AccountType.objects.get_or_create(category='equity',    defaults={'normal_balance': normal['equity']})
at_rev,   _ = AccountType.objects.get_or_create(category='revenue',   defaults={'normal_balance': normal['revenue']})
at_exp,   _ = AccountType.objects.get_or_create(category='expense',   defaults={'normal_balance': normal['expense']})
print('✓ Account types')

# ── Chart of Accounts ──────────────────────
acc_defs = [
    ('1000', 'الصندوق النقدي',       at_asset),
    ('1010', 'البنك الأهلي',         at_asset),
    ('1020', 'البنك الراجحي',        at_asset),
    ('1100', 'العملاء - ذمم مدينة',  at_asset),
    ('1200', 'المخزون',              at_asset),
    ('1500', 'الأصول الثابتة',       at_asset),
    ('2000', 'الموردون - ذمم دائنة', at_liab),
    ('2100', 'قروض بنكية',           at_liab),
    ('2200', 'مستحقات الموظفين',     at_liab),
    ('3000', 'رأس المال',            at_eq),
    ('3100', 'الأرباح المبقاة',      at_eq),
    ('4000', 'إيرادات المشاريع',     at_rev),
    ('4100', 'إيرادات استشارية',     at_rev),
    ('5000', 'تكلفة المشاريع',       at_exp),
    ('5100', 'رواتب وأجور',          at_exp),
    ('5200', 'إيجارات',              at_exp),
    ('5300', 'مصروفات عامة',         at_exp),
    ('5400', 'استهلاك الأصول',       at_exp),
]
acc = {}
for code, name, atype in acc_defs:
    a, _ = Account.objects.get_or_create(code=code, defaults={
        'name': name, 'account_type': atype, 'is_system': True,
    })
    acc[code] = a
print('✓ Chart of accounts (%d)' % len(acc))

# ── Cost Centers ───────────────────────────
cc_adm,  _ = CostCenter.objects.get_or_create(name='الإدارة العامة',      defaults={'code': 'CC-ADM', 'type': 'admin'})
cc_p1,   _ = CostCenter.objects.get_or_create(name='مشروع جامع النور',    defaults={'code': 'CC-P01', 'type': 'project'})
cc_p2,   _ = CostCenter.objects.get_or_create(name='مشروع عمارة الرياض', defaults={'code': 'CC-P02', 'type': 'project'})
print('✓ Cost centers')

# ── Accounting Periods ─────────────────────
for yr, mo, st in [
    (2025, 11, 'closed'), (2025, 12, 'closed'),
    (2026,  1, 'closed'), (2026,  2, 'closed'),
    (2026,  3, 'closed'), (2026,  4, 'open'),
    (2026,  5, 'open'),   (2026,  6, 'open'),
]:
    AccountingPeriod.objects.get_or_create(year=yr, month=mo, defaults={'status': st})
print('✓ Accounting periods')

# ── Journals ───────────────────────────────
def journal(dt, desc, src, cc, lines, posted=True):
    j = Journal.objects.create(date=dt, description=desc, source_type=src, cost_center=cc)
    for code, dr, cr, note in lines:
        JournalLine.objects.create(journal=j, account=acc[code],
                                   debit=D(str(dr)), credit=D(str(cr)), note=note)
    if posted:
        j.is_posted = True
        j.save(update_fields=['is_posted'])

journal(date(2026, 1,  5), 'رأس المال المرحّل - يناير 2026',                'manual',      cc_adm, [
    ('1010', 500000, 0,      'رصيد افتتاحي بنك الأهلي'),
    ('3000', 0,      500000, 'رأس المال'),
])
journal(date(2026, 1,  8), 'استلام دفعة 40٪ من عميل جامع النور',           'receipt',     cc_p1, [
    ('1010', 180000, 0,      'تحويل للبنك الأهلي'),
    ('1100', 0,      180000, 'تسوية ذمة العميل'),
])
journal(date(2026, 1, 12), 'شراء مواد بناء وحديد تسليح للمشروع',           'purchase',    cc_p1, [
    ('5000', 95000,  0,      'تكلفة مواد'),
    ('2000', 0,      95000,  'مستحق للمورد'),
])
journal(date(2026, 1, 31), 'رواتب الموظفين - يناير 2026',                  'payroll',     cc_adm, [
    ('5100', 62000,  0,      'رواتب شهر يناير'),
    ('2200', 0,      62000,  'مستحقات للموظفين'),
])
journal(date(2026, 2,  3), 'استلام دفعة أولى من مشروع عمارة الرياض',      'receipt',     cc_p2, [
    ('1010', 250000, 0,      'تحويل للبنك الأهلي'),
    ('1100', 0,      250000, 'تسوية ذمة العميل'),
])
journal(date(2026, 2, 10), 'تسوية مع المورد - شركة حديد العرب',           'payment',     cc_p1, [
    ('2000', 95000,  0,      'تسوية الذمة الدائنة'),
    ('1020', 0,      95000,  'خصم من بنك الراجحي'),
])
journal(date(2026, 2, 15), 'إيجار مكتب الإدارة - فبراير 2026',            'manual',      cc_adm, [
    ('5200', 12000,  0,      'إيجار شهري'),
    ('1010', 0,      12000,  'خصم من البنك الأهلي'),
])
journal(date(2026, 2, 28), 'رواتب الموظفين - فبراير 2026',                'payroll',     cc_adm, [
    ('5100', 62000,  0,      'رواتب شهر فبراير'),
    ('2200', 0,      62000,  'مستحقات للموظفين'),
])
journal(date(2026, 3,  1), 'إيراد مشروع جامع النور - المرحلة الثانية',    'invoice',     cc_p1, [
    ('1100', 320000, 0,      'فاتورة المرحلة الثانية'),
    ('4000', 0,      320000, 'إيراد المشروع'),
])
journal(date(2026, 3, 10), 'استهلاك أصول ثابتة - مارس 2026',              'depreciation',cc_adm, [
    ('5400', 8500,   0,      'استهلاك آليات ومعدات'),
    ('1500', 0,      8500,   'تراكم الاستهلاك'),
])
journal(date(2026, 3, 20), 'شراء معدات إضافية للمشروع',                   'purchase',    cc_p2, [
    ('5000', 42000,  0,      'معدات وعدة'),
    ('2000', 0,      42000,  'مستحق للمورد'),
])
journal(date(2026, 3, 31), 'رواتب الموظفين - مارس 2026',                  'payroll',     cc_adm, [
    ('5100', 62000,  0,      'رواتب شهر مارس'),
    ('2200', 0,      62000,  'مستحقات للموظفين'),
])
journal(date(2026, 4,  5), 'دفعة للمورد - مواد تشطيب',                    'payment',     cc_p2, [
    ('2000', 42000,  0,      'تسوية الذمة'),
    ('1020', 0,      42000,  'خصم من بنك الراجحي'),
])
journal(date(2026, 4, 18), 'إيراد مشروع عمارة الرياض - تسليم جزئي',      'invoice',     cc_p2, [
    ('1100', 480000, 0,      'فاتورة التسليم الجزئي'),
    ('4000', 0,      480000, 'إيراد المشروع'),
])
journal(date(2026, 5,  2), 'مصروفات عامة وقرطاسية - أبريل',              'manual',      cc_adm, [
    ('5300', 9800,   0,      'مصروفات متنوعة'),
    ('1000', 0,      9800,   'صرف نقدي'),
], posted=False)
print('✓ Journals (15)')

# ── Fixed Assets ───────────────────────────
assets = [
    ('حفار كاتربيلر 320D',    'heavy_equipment', date(2024,3,15), D('420000'), 120, D('30000'), cc_p1,  'مستخدم في مشاريع الحفر والتأسيس'),
    ('لودر كوماتسو WA380',    'heavy_equipment', date(2024,6,1),  D('280000'), 96,  D('20000'), cc_p2,  ''),
    ('رافعة برجية 25 طن',     'heavy_equipment', date(2023,8,15), D('650000'), 144, D('50000'), cc_p1,  'رافعة ثابتة للبناء العمودي'),
    ('شاحنة نقل فريتلاينر',  'vehicles',        date(2023,9,10), D('185000'), 72,  D('15000'), cc_adm, 'نقل مواد بين المشاريع'),
    ('دبابة ماء 10 طن',       'vehicles',        date(2025,1,20), D('95000'),  60,  D('5000'),  cc_p1,  ''),
    ('سيارة مدير المشاريع',   'vehicles',        date(2024,11,5), D('145000'), 60,  D('10000'), cc_adm, 'لاند كروزر 2024'),
    ('خلاطة خرسانة 500L',    'tools',           date(2024,8,5),  D('35000'),  48,  D('2000'),  cc_p2,  ''),
    ('مولد كهربائي 100KW',   'tools',           date(2023,11,1), D('62000'),  60,  D('5000'),  cc_p1,  ''),
    ('معدات سباكة وكهرباء',   'tools',           date(2025,2,10), D('28000'),  36,  D('2000'),  cc_p2,  ''),
    ('أجهزة حاسب آلي 5',     'it_equipment',    date(2025,3,1),  D('22000'),  36,  D('2000'),  cc_adm, ''),
    ('طابعات وسكانرات',       'it_equipment',    date(2025,3,1),  D('8500'),   24,  D('500'),   cc_adm, ''),
    ('أثاث مكتب الإدارة',    'furniture',       date(2024,1,15), D('18000'),  60,  D('1000'),  cc_adm, ''),
    ('أثاث غرفة الاجتماعات', 'furniture',       date(2024,1,15), D('12000'),  60,  D('500'),   cc_adm, ''),
]
for name, cat, pdate, cost, life, salv, cc, notes in assets:
    FixedAsset.objects.get_or_create(name=name, defaults={
        'category': cat, 'purchase_date': pdate, 'cost': cost,
        'useful_life_months': life, 'salvage_value': salv,
        'cost_center': cc, 'notes': notes,
    })
print('✓ Fixed assets (%d)' % len(assets))

# ── Payroll Runs ───────────────────────────
emps = list(Employee.objects.all())
emp_data = [
    (18000, 3000,  0,   0,    ''),
    (12000, 2000,  500, 0,    'استقطاع غياب'),
    (11000, 2000,  0,   0,    ''),
    (8500,  1500,  0,   1000, 'بونص إنجاز'),
    (7000,  1000,  0,   0,    ''),
    (5500,  800,   0,   0,    ''),
    (6000,  900,   0,   500,  'بونص أداء'),
    (9500,  1500,  0,   0,    ''),
]
for yr, mo, status in [(2026,1,'posted'),(2026,2,'posted'),(2026,3,'posted'),(2026,4,'draft')]:
    pr, created = PayrollRun.objects.get_or_create(year=yr, month=mo, defaults={'status': status})
    if created and emps:
        tg = tn = D('0')
        for i, emp in enumerate(emps[:len(emp_data)]):
            basic, allow, ded, bonus, ded_r = emp_data[i]
            b, a, d, bon = D(str(basic)), D(str(allow)), D(str(ded)), D(str(bonus))
            PayrollLine.objects.create(
                payroll=pr, employee=emp,
                basic=b, allowances=a, deductions=d, bonus=bon,
                deduction_note=ded_r,
            )
            tg += b + a + bon
            tn += b + a + bon - d
        pr.total_gross = tg
        pr.total_net   = tn
        pr.save(update_fields=['total_gross', 'total_net'])
print('✓ Payroll runs (4)')

# ═══════════════════════════════════════════
# INVENTORY
# ═══════════════════════════════════════════
from inventory.models import (
    ItemCategory, Warehouse, Item, Supplier,
    PurchaseOrder, PurchaseOrderLine, StockMovement, Alert,
)
from django.contrib.auth.models import User
admin_user = User.objects.filter(is_superuser=True).first()

# ── Item Categories ────────────────────────
cats = {
    'materials':  ItemCategory.objects.get_or_create(name='مواد البناء',    defaults={'type': 'materials'})[0],
    'tools':      ItemCategory.objects.get_or_create(name='أدوات وعدد',     defaults={'type': 'tools'})[0],
    'equipment':  ItemCategory.objects.get_or_create(name='معدات',          defaults={'type': 'equipment'})[0],
    'consumable': ItemCategory.objects.get_or_create(name='مستهلكات',       defaults={'type': 'consumable'})[0],
    'safety':     ItemCategory.objects.get_or_create(name='معدات السلامة',  defaults={'type': 'safety'})[0],
}
print('✓ Item categories')

# ── Warehouses ─────────────────────────────
wh_main,  _ = Warehouse.objects.get_or_create(name='المستودع الرئيسي',      defaults={'location': 'المنطقة الصناعية - الرياض'})
wh_north, _ = Warehouse.objects.get_or_create(name='مستودع شمال الرياض',   defaults={'location': 'حي النسيم - الرياض'})
wh_site1, _ = Warehouse.objects.get_or_create(name='مخزن موقع جامع النور', defaults={'location': 'موقع المشروع - الرياض'})
wh_site2, _ = Warehouse.objects.get_or_create(name='مخزن عمارة الرياض',    defaults={'location': 'موقع المشروع - الرياض'})
print('✓ Warehouses')

# ── Items ──────────────────────────────────
item_defs = [
    # (warehouse, category, name, sku, unit, qty, reorder, cost)
    (wh_main,  'materials',  'أسمنت بورتلاند 50 كجم',       'CEM-001', 'كيس',    350, 100, D('28')),
    (wh_main,  'materials',  'حديد تسليح 12مم',              'STL-012', 'طن',      18,   5,  D('3800')),
    (wh_main,  'materials',  'حديد تسليح 16مم',              'STL-016', 'طن',      12,   5,  D('3850')),
    (wh_main,  'materials',  'رمل خشن',                      'SND-001', 'م³',      80,  20,  D('45')),
    (wh_main,  'materials',  'حصى ناعم 10مم',                'GRV-001', 'م³',      60,  15,  D('55')),
    (wh_main,  'materials',  'طوب أحمر',                     'BRK-001', 'ألف قطعة', 25,   5,  D('320')),
    (wh_main,  'materials',  'بلاط سيراميك 60×60',          'CRM-001', 'م²',     200,  50,  D('32')),
    (wh_main,  'materials',  'دهان أبيض داخلي',              'PNT-001', 'لتر',    180,  40,  D('12')),
    (wh_main,  'materials',  'أنابيب PVC 4 بوصة',           'PVC-004', 'متر',    120,  30,  D('18')),
    (wh_main,  'materials',  'كابلات كهربائية 6مم',         'CBL-006', 'متر',    500, 100,  D('8')),
    (wh_north, 'materials',  'ألواح خشب قالب',               'WOD-001', 'م²',      90,  20,  D('25')),
    (wh_north, 'materials',  'عزل مائي رول',                 'INS-001', 'رول',     40,  10,  D('85')),
    (wh_north, 'materials',  'زجاج عادي 6مم',               'GLS-001', 'م²',      60,  15,  D('45')),
    (wh_site1, 'tools',      'مسمار 4 بوصة',                 'NLS-004', 'كجم',     25,  10,  D('15')),
    (wh_site1, 'tools',      'صواميل ومسامير متنوعة',        'NLS-MIX', 'كجم',     15,   5,  D('22')),
    (wh_site1, 'tools',      'فرامات حديد',                  'CUT-001', 'قطعة',     4,   2,  D('180')),
    (wh_site1, 'equipment',  'مضخة مياه 2 بوصة',            'PMP-002', 'قطعة',     2,   1,  D('850')),
    (wh_site1, 'equipment',  'وينش كهربائي 1 طن',           'HIS-001', 'قطعة',     1,   1,  D('4200')),
    (wh_site2, 'consumable', 'قفازات حماية',                 'GLV-001', 'زوج',     60,  20,  D('8')),
    (wh_site2, 'consumable', 'خوذات السلامة',                'HLM-001', 'قطعة',    15,   5,  D('35')),
    (wh_site2, 'safety',     'سترات عاكسة',                  'VES-001', 'قطعة',    12,   5,  D('28')),
    (wh_site2, 'safety',     'نظارات واقية',                 'GGL-001', 'قطعة',    10,   4,  D('22')),
    (wh_site2, 'safety',     'حذاء سلامة',                   'SHO-001', 'زوج',      8,   4,  D('95')),
    (wh_main,  'consumable', 'زيت مكينة موبيل 5W-40',       'OIL-001', 'لتر',     30,  10,  D('28')),
    (wh_main,  'consumable', 'فلاتر هواء معدات ثقيلة',      'FLT-001', 'قطعة',     8,   3,  D('120')),
]
items_map = {}
for wh, cat_key, name, sku, unit, qty, reorder, cost in item_defs:
    it, _ = Item.objects.get_or_create(sku=sku, defaults={
        'warehouse': wh, 'category': cats[cat_key],
        'name': name, 'unit': unit,
        'qty_on_hand': D(str(qty)), 'reorder_level': D(str(reorder)),
        'unit_cost': cost,
    })
    items_map[sku] = it
print('✓ Items (%d)' % len(item_defs))

# ── Suppliers ──────────────────────────────
sup_defs = [
    ('شركة حديد العرب',         'أحمد الزهراني',   '0501234567', 'steel@arabiron.com',     'المورد الرئيسي للحديد'),
    ('مصنع الأسمنت السعودي',   'محمد العتيبي',    '0559876543', 'cement@saudicement.com', 'أسمنت بورتلاند وسريع التصلب'),
    ('شركة المواد الإنشائية',   'خالد الدوسري',    '0533334444', 'info@buildmat.sa',       'مواد بناء متنوعة'),
    ('مؤسسة السلامة للمعدات',  'فيصل القحطاني',   '0545556666', 'safety@safetyco.sa',     'معدات السلامة والحماية'),
    ('شركة الكهرباء والتمديدات','عبدالله المالكي',  '0567778888', 'elec@wiring.sa',         'كابلات وأدوات كهربائية'),
    ('مستودعات البناء العصري',  'سلطان الشمري',    '0512223333', 'orders@modernbuild.sa',  'مواد تشطيب وديكور'),
]
sups = []
for name, contact, phone, email, notes in sup_defs:
    s, _ = Supplier.objects.get_or_create(name=name, defaults={
        'contact_name': contact, 'phone': phone, 'email': email, 'notes': notes,
    })
    sups.append(s)
print('✓ Suppliers (%d)' % len(sups))

# ── Purchase Orders ────────────────────────
po_defs = [
    (sups[0], date(2026,1,10), date(2026,1,20), 'received', [
        ('STL-012', 5,  D('3800')),
        ('STL-016', 3,  D('3850')),
    ]),
    (sups[1], date(2026,1,15), date(2026,1,25), 'received', [
        ('CEM-001', 200, D('28')),
    ]),
    (sups[2], date(2026,2,5),  date(2026,2,15), 'received', [
        ('SND-001', 30,  D('45')),
        ('GRV-001', 20,  D('55')),
        ('BRK-001', 10,  D('320')),
    ]),
    (sups[4], date(2026,2,20), date(2026,3,1),  'received', [
        ('CBL-006', 300, D('8')),
        ('PVC-004', 80,  D('18')),
    ]),
    (sups[3], date(2026,3,10), date(2026,3,20), 'received', [
        ('GLV-001', 40,  D('8')),
        ('HLM-001', 10,  D('35')),
        ('VES-001', 8,   D('28')),
        ('SHO-001', 5,   D('95')),
    ]),
    (sups[5], date(2026,4,1),  date(2026,4,15), 'received', [
        ('CRM-001', 100, D('32')),
        ('GLS-001', 40,  D('45')),
    ]),
    (sups[0], date(2026,5,10), date(2026,5,25), 'pending', [
        ('STL-012', 8,  D('3900')),
        ('STL-016', 5,  D('3950')),
    ]),
    (sups[1], date(2026,5,15), date(2026,5,30), 'pending', [
        ('CEM-001', 300, D('29')),
        ('SND-001', 40,  D('46')),
    ]),
]
for sup, odate, edate, status, lines in po_defs:
    total = sum(qty * price for _, qty, price in lines)
    po, created = PurchaseOrder.objects.get_or_create(
        supplier=sup, order_date=odate,
        defaults={
            'expected_date': edate, 'status': status,
            'total_amount': total, 'created_by': admin_user,
        }
    )
    if created:
        for sku, qty, price in lines:
            qr = D(str(qty))
            PurchaseOrderLine.objects.create(
                order=po, item=items_map[sku],
                qty_ordered=qr,
                qty_received=qr if status == 'received' else D('0'),
                unit_price=price,
            )
print('✓ Purchase orders (%d)' % len(po_defs))

# ── Stock Movements ────────────────────────
mov_defs = [
    ('CEM-001', 'in',     D('200'),  'استلام من أمر شراء PO-0002', 'جامع النور'),
    ('STL-012', 'in',     D('5'),    'استلام من أمر شراء PO-0001', 'جامع النور'),
    ('STL-016', 'in',     D('3'),    'استلام من أمر شراء PO-0001', 'جامع النور'),
    ('CEM-001', 'out',    D('-80'),  'صرف للموقع - خرسانة الأساسات', 'جامع النور'),
    ('STL-012', 'out',    D('-2'),   'صرف للموقع - حديد الأساسات',  'جامع النور'),
    ('SND-001', 'in',     D('30'),   'استلام من أمر شراء PO-0003',  'عمارة الرياض'),
    ('GRV-001', 'in',     D('20'),   'استلام من أمر شراء PO-0003',  'عمارة الرياض'),
    ('SND-001', 'out',    D('-15'),  'صرف للموقع - خلط خرسانة',     'عمارة الرياض'),
    ('GLV-001', 'in',     D('40'),   'استلام معدات سلامة',           'عمارة الرياض'),
    ('HLM-001', 'in',     D('10'),   'استلام خوذات',                 'جامع النور'),
    ('CRM-001', 'in',     D('100'),  'استلام بلاط',                  'عمارة الرياض'),
    ('CBL-006', 'in',     D('300'),  'استلام كابلات كهربائية',       'جامع النور'),
    ('CBL-006', 'out',    D('-120'), 'صرف للأسلاك الكهربائية',       'جامع النور'),
    ('PNT-001', 'out',    D('-40'),  'صرف دهان للأدوار الأولى',      'عمارة الرياض'),
    ('OIL-001', 'out',    D('-8'),   'زيت للحفار - صيانة شهرية',    'جامع النور'),
    ('FLT-001', 'out',    D('-2'),   'فلتر هواء للودر',              'عمارة الرياض'),
    ('NLS-004', 'in',     D('25'),   'استلام مسامير',                'جامع النور'),
    ('NLS-004', 'out',    D('-8'),   'صرف للنجارة',                  'جامع النور'),
]
for sku, mtype, qty, reason, project in mov_defs:
    StockMovement.objects.get_or_create(
        item=items_map[sku], move_type=mtype, qty=qty,
        defaults={
            'performed_by': admin_user,
            'reason': reason,
            'project': project,
        }
    )
print('✓ Stock movements (%d)' % len(mov_defs))

# ── Alerts ─────────────────────────────────
low_items = Item.objects.filter(qty_on_hand__lte=10)
for it in low_items:
    Alert.objects.get_or_create(item=it, alert_type='low_stock', status='active')
# expiry soon
expiry_items = Item.objects.filter(expiry_date__isnull=False)
for it in expiry_items:
    Alert.objects.get_or_create(item=it, alert_type='expiry_soon', status='active')
print('✓ Alerts created')

print('\n✅ All seed data complete!')
EOF