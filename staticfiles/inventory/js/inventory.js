/* inventory.js */
'use strict';

/* ── sidebar ── */
(function(){
    const sb  = document.getElementById('sidebar');
    const btn = document.getElementById('sidebarToggle');
    if(!sb || !btn) return;

    function setExpanded(expanded){
        sb.classList.toggle('expanded', expanded);
        document.body.classList.toggle('sidebar-open', expanded);
        localStorage.setItem('sidebar_expanded', expanded ? '1' : '0');
    }

    setExpanded(localStorage.getItem('sidebar_expanded') === '1');

    btn.addEventListener('click', function(){
        setExpanded(!sb.classList.contains('expanded'));
    });

    document.addEventListener('keydown', function(e){
        if((e.key === '[' || e.key === 'b') && !e.target.matches('input,textarea')){
            setExpanded(!sb.classList.contains('expanded'));
        }
    });
})();

/* ── tabs ── */
document.querySelectorAll('.inv-tab').forEach(function(tab){
    tab.addEventListener('click', function(){
        document.querySelectorAll('.inv-tab').forEach(function(t){ t.classList.remove('active'); });
        document.querySelectorAll('.inv-section').forEach(function(s){ s.classList.remove('active'); });
        tab.classList.add('active');
        var sec = document.getElementById('tab-' + tab.dataset.tab);
        if(sec) sec.classList.add('active');
        var barId = 'pag-' + tab.dataset.tab;
        var tbody = document.querySelector('#tab-' + tab.dataset.tab + ' tbody');
        if(tbody && PAG_MAP[barId]) renderPag(barId, tbody);
    });
});

/* ── live search ── */
document.querySelectorAll('.inv-search').forEach(function(input){
    input.addEventListener('input', function(){
        var q = input.value.trim().toLowerCase();
        var tbody = document.querySelector('#tab-' + input.dataset.target + ' tbody');
        if(!tbody) return;
        tbody.querySelectorAll('tr').forEach(function(row){
            row.style.display = q && !row.textContent.toLowerCase().includes(q) ? 'none' : '';
        });
        var barId = 'pag-' + input.dataset.target;
        _pages[barId] = 1;
        renderPag(barId, tbody);
    });
});

/* ── helpers ── */
function post(url, data){
    return fetch(url, {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': CSRF},
        body: JSON.stringify(data)
    }).then(function(r){ return r.json(); });
}

function showErr(msg){ alert('خطأ: ' + msg); }

function openPanel(overlayId, panelId){
    document.getElementById(overlayId).classList.add('active');
    document.getElementById(panelId).classList.add('active');
}
function closePanel(overlayId, panelId){
    document.getElementById(overlayId).classList.remove('active');
    document.getElementById(panelId).classList.remove('active');
}

/* delete confirm */
var _delUrl = '', _delCallback = null;
function setPending(url, name, callback){
    _delUrl = url; _delCallback = callback || null;
    document.getElementById('delName').textContent = name;
    document.getElementById('invDelOverlay').classList.add('active');
    document.getElementById('invDelModal').classList.add('active');
}
function closeDel(){
    document.getElementById('invDelOverlay').classList.remove('active');
    document.getElementById('invDelModal').classList.remove('active');
}
document.getElementById('delCancelBtn').addEventListener('click', closeDel);
document.getElementById('delConfirmBtn').addEventListener('click', function(){
    post(_delUrl, {}).then(function(r){
        if(r.ok){ closeDel(); location.reload(); }
        else showErr(r.error);
    });
});

/* ════════════════════════════════
   WAREHOUSES
════════════════════════════════ */
function openAddWarehouse(){
    document.getElementById('whModalTitle').textContent = 'مستودع جديد';
    document.getElementById('editWhId').value = '';
    document.getElementById('whForm').reset();
    openPanel('whOverlay','whPanel');
}
function closeWhModal(){ closePanel('whOverlay','whPanel'); }
document.getElementById('whOverlay').addEventListener('click', closeWhModal);

function editWarehouse(id, name, location, notes){
    document.getElementById('whModalTitle').textContent = 'تعديل المستودع';
    document.getElementById('editWhId').value = id;
    document.getElementById('whName').value = name;
    document.getElementById('whLocation').value = location;
    document.getElementById('whNotes').value = notes;
    openPanel('whOverlay','whPanel');
}

function submitWarehouse(){
    var id   = document.getElementById('editWhId').value;
    var name = document.getElementById('whName').value.trim();
    if(!name) return showErr('اسم المستودع مطلوب');
    var url  = id ? URL_WH_EDIT.replace('0', id) : URL_WH_CREATE;
    post(url, {
        name:     name,
        location: document.getElementById('whLocation').value.trim(),
        notes:    document.getElementById('whNotes').value.trim(),
    }).then(function(r){
        if(r.ok) location.reload();
        else showErr(r.error);
    });
}

/* ════════════════════════════════
   ITEMS
════════════════════════════════ */
function openAddItem(){
    document.getElementById('itemModalTitle').textContent = 'صنف جديد';
    document.getElementById('editItemId').value = '';
    document.getElementById('itemForm').reset();
    openPanel('itemOverlay','itemPanel');
}
function closeItemModal(){ closePanel('itemOverlay','itemPanel'); }
document.getElementById('itemOverlay').addEventListener('click', closeItemModal);

function editItem(id, warehouseId, categoryId, name, sku, unit, qty, reorder, cost, expiry, notes){
    document.getElementById('itemModalTitle').textContent = 'تعديل الصنف';
    document.getElementById('editItemId').value = id;
    document.getElementById('iWarehouse').value = warehouseId;
    document.getElementById('iCategory').value  = categoryId || '';
    document.getElementById('iName').value      = name;
    document.getElementById('iSku').value       = sku;
    document.getElementById('iUnit').value      = unit;
    document.getElementById('iQty').value       = qty;
    document.getElementById('iReorder').value   = reorder;
    document.getElementById('iCost').value      = cost;
    document.getElementById('iExpiry').value    = expiry;
    document.getElementById('iNotes').value     = notes;
    openPanel('itemOverlay','itemPanel');
}

function submitItem(){
    var id = document.getElementById('editItemId').value;
    var name = document.getElementById('iName').value.trim();
    if(!name) return showErr('اسم الصنف مطلوب');
    var url = id ? URL_ITEM_EDIT.replace('0', id) : URL_ITEM_CREATE;
    post(url, {
        warehouse_id:  document.getElementById('iWarehouse').value,
        category_id:   document.getElementById('iCategory').value || null,
        name:          name,
        sku:           document.getElementById('iSku').value.trim(),
        unit:          document.getElementById('iUnit').value.trim(),
        qty_on_hand:   parseFloat(document.getElementById('iQty').value) || 0,
        reorder_level: parseFloat(document.getElementById('iReorder').value) || 0,
        unit_cost:     parseFloat(document.getElementById('iCost').value) || 0,
        expiry_date:   document.getElementById('iExpiry').value || null,
        notes:         document.getElementById('iNotes').value.trim(),
    }).then(function(r){
        if(r.ok) location.reload();
        else showErr(r.error);
    });
}

/* ════════════════════════════════
   SUPPLIERS
════════════════════════════════ */
function openAddSupplier(){
    document.getElementById('supModalTitle').textContent = 'مورد جديد';
    document.getElementById('editSupId').value = '';
    document.getElementById('supForm').reset();
    openPanel('supOverlay','supPanel');
}
function closeSupModal(){ closePanel('supOverlay','supPanel'); }
document.getElementById('supOverlay').addEventListener('click', closeSupModal);

function editSupplier(id, name, contact, phone, email, notes){
    document.getElementById('supModalTitle').textContent = 'تعديل المورد';
    document.getElementById('editSupId').value   = id;
    document.getElementById('sName').value       = name;
    document.getElementById('sContact').value    = contact;
    document.getElementById('sPhone').value      = phone;
    document.getElementById('sEmail').value      = email;
    document.getElementById('sNotes').value      = notes;
    openPanel('supOverlay','supPanel');
}

function submitSupplier(){
    var id   = document.getElementById('editSupId').value;
    var name = document.getElementById('sName').value.trim();
    if(!name) return showErr('اسم المورد مطلوب');
    var url  = id ? URL_SUP_EDIT.replace('0', id) : URL_SUP_CREATE;
    post(url, {
        name:         name,
        contact_name: document.getElementById('sContact').value.trim(),
        phone:        document.getElementById('sPhone').value.trim(),
        email:        document.getElementById('sEmail').value.trim(),
        notes:        document.getElementById('sNotes').value.trim(),
    }).then(function(r){
        if(r.ok) location.reload();
        else showErr(r.error);
    });
}

/* ════════════════════════════════
   PURCHASE ORDERS
════════════════════════════════ */
function openAddPO(){
    document.getElementById('poForm').reset();
    document.getElementById('poLinesBody').innerHTML = '';
    addPOLine();
    openPanel('poOverlay','poPanel');
}
function closePOModal(){ closePanel('poOverlay','poPanel'); }
document.getElementById('poOverlay').addEventListener('click', closePOModal);

function addPOLine(){
    var tr = document.createElement('tr');
    tr.innerHTML =
        '<td><select class="po-line-item" required><option value="">اختر صنف...</option>' + ITEMS_OPTIONS + '</select></td>' +
        '<td><input type="number" class="po-line-qty" min="0" step="0.01" placeholder="0"></td>' +
        '<td><input type="number" class="po-line-price" min="0" step="0.01" placeholder="0.00"></td>' +
        '<td style="text-align:center"><button type="button" onclick="this.closest(\'tr\').remove()" style="background:none;border:none;color:#ef4444;cursor:pointer;font-size:16px;">×</button></td>';
    document.getElementById('poLinesBody').appendChild(tr);
}

function submitPO(){
    var supplierId = document.getElementById('poSupplier').value;
    if(!supplierId) return showErr('المورد مطلوب');
    var lines = [];
    document.querySelectorAll('#poLinesBody tr').forEach(function(tr){
        var itemId = tr.querySelector('.po-line-item').value;
        var qty    = parseFloat(tr.querySelector('.po-line-qty').value) || 0;
        var price  = parseFloat(tr.querySelector('.po-line-price').value) || 0;
        if(itemId && qty > 0) lines.push({item_id: itemId, qty: qty, unit_price: price});
    });
    if(!lines.length) return showErr('أضف بند واحد على الأقل');
    post(URL_PO_CREATE, {
        supplier_id:   supplierId,
        expected_date: document.getElementById('poExpected').value || null,
        notes:         document.getElementById('poNotes').value.trim(),
        lines:         lines,
    }).then(function(r){
        if(r.ok) location.reload();
        else showErr(r.error);
    });
}

function viewPO(id){
    fetch(URL_PO_DETAIL.replace('0', id)).then(function(r){ return r.json(); }).then(function(d){
        if(!d.ok) return showErr(d.error);
        var html = '<div class="view-meta">' +
            '<div class="view-meta-item"><div class="view-meta-label">رقم الأمر</div><div class="view-meta-val">' + d.ref + '</div></div>' +
            '<div class="view-meta-item"><div class="view-meta-label">المورد</div><div class="view-meta-val">' + d.supplier + '</div></div>' +
            '<div class="view-meta-item"><div class="view-meta-label">الحالة</div><div class="view-meta-val">' + d.status + '</div></div>' +
            '<div class="view-meta-item"><div class="view-meta-label">تاريخ الطلب</div><div class="view-meta-val">' + d.order_date + '</div></div>' +
            (d.expected_date ? '<div class="view-meta-item"><div class="view-meta-label">تاريخ الاستلام المتوقع</div><div class="view-meta-val">' + d.expected_date + '</div></div>' : '') +
            '<div class="view-meta-item"><div class="view-meta-label">الإجمالي (ريال)</div><div class="view-meta-val" style="color:var(--gold)">' + d.total_amount.toFixed(2) + '</div></div>' +
            '</div>';
        if(d.lines.length){
            html += '<table class="inv-table" style="margin-top:8px"><thead><tr><th>الصنف</th><th>الوحدة</th><th>مطلوب</th><th>مستلم</th><th>سعر الوحدة</th><th>الإجمالي</th></tr></thead><tbody>';
            d.lines.forEach(function(ln){
                html += '<tr><td>' + ln.item_name + '</td><td>' + ln.unit + '</td><td>' + ln.qty_ordered + '</td><td>' + ln.qty_received + '</td><td>' + ln.unit_price.toFixed(2) + '</td><td style="font-weight:700">' + ln.line_total.toFixed(2) + '</td></tr>';
            });
            html += '</tbody></table>';
        }
        if(d.notes) html += '<p style="margin-top:14px;font-size:13px;color:var(--text-muted)">' + d.notes + '</p>';
        document.getElementById('poViewBody').innerHTML = html;
        openPanel('poViewOverlay','poViewPanel');
    });
}
function closePOView(){ closePanel('poViewOverlay','poViewPanel'); }
document.getElementById('poViewOverlay').addEventListener('click', closePOView);

function receivePO(id, ref){
    if(!confirm('تأكيد استلام جميع بنود ' + ref + '؟')) return;
    post(URL_PO_RECEIVE.replace('0', id), {}).then(function(r){
        if(r.ok) location.reload();
        else showErr(r.error);
    });
}

function cancelPO(id, ref){
    if(!confirm('إلغاء ' + ref + '؟')) return;
    post(URL_PO_CANCEL.replace('0', id), {}).then(function(r){
        if(r.ok) location.reload();
        else showErr(r.error);
    });
}

/* ════════════════════════════════
   STOCK MOVEMENTS
════════════════════════════════ */
function openAddMovement(){
    document.getElementById('movForm').reset();
    openPanel('movOverlay','movPanel');
}
function closeMovModal(){ closePanel('movOverlay','movPanel'); }
document.getElementById('movOverlay').addEventListener('click', closeMovModal);

function submitMovement(){
    var itemId    = document.getElementById('mItem').value;
    var moveType  = document.getElementById('mType').value;
    var qty       = parseFloat(document.getElementById('mQty').value) || 0;
    if(!itemId || !moveType || qty <= 0) return showErr('بيانات غير مكتملة');
    post(URL_MOV_CREATE, {
        item_id:   itemId,
        move_type: moveType,
        qty:       qty,
        reason:    document.getElementById('mReason').value.trim(),
        project:   document.getElementById('mProject').value.trim(),
    }).then(function(r){
        if(r.ok) location.reload();
        else showErr(r.error);
    });
}

/* ════════════════════════════════
   ALERTS
════════════════════════════════ */
function resolveAlert(id){
    post(URL_ALERT_RESOLVE.replace('0', id), {}).then(function(r){
        if(r.ok) location.reload();
        else showErr(r.error);
    });
}

/* ════════════════════════════════
   PAGINATION
════════════════════════════════ */
var PAGE_SIZE = 10;
var _pages = {};

function renderPag(barId, tbody){
    var bar = document.getElementById(barId);
    if(!bar || !tbody) return;
    var allRows = Array.prototype.slice.call(tbody.rows);
    // rows not explicitly hidden by search
    var showable = allRows.filter(function(r){ return r.style.display !== 'none'; });
    if(!showable.length){ bar.innerHTML = ''; return; }

    var total = showable.length;
    var pages = Math.max(1, Math.ceil(total / PAGE_SIZE));
    var cur   = Math.min(_pages[barId] || 1, pages);
    _pages[barId] = cur;

    // hide all, then show current page slice
    allRows.forEach(function(r){ r.style.display = 'none'; });
    showable.slice((cur - 1) * PAGE_SIZE, cur * PAGE_SIZE).forEach(function(r){ r.style.display = ''; });

    bar.innerHTML = '';
    if(pages <= 1 && total <= PAGE_SIZE) return;

    function mkBtn(label, page, isActive, disabled){
        var b = document.createElement('button');
        b.className = 'pag-btn' + (isActive ? ' active' : '');
        b.textContent = label;
        b.disabled = disabled;
        if(!disabled && !isActive) b.onclick = function(){ _pages[barId] = page; renderPag(barId, tbody); };
        return b;
    }

    bar.appendChild(mkBtn('السابق', cur - 1, false, cur <= 1));

    var startP = Math.max(1, cur - 2);
    var endP   = Math.min(pages, startP + 4);
    for(var p = startP; p <= endP; p++){
        bar.appendChild(mkBtn(String(p), p, p === cur, false));
    }

    bar.appendChild(mkBtn('التالي', cur + 1, false, cur >= pages));

    var info = document.createElement('span');
    info.className = 'pag-info';
    info.textContent = 'صفحة ' + cur + ' من ' + pages + ' (' + total + ' سجل)';
    bar.appendChild(info);
}

function initPagination(){
    Object.keys(PAG_MAP).forEach(function(barId){
        var tbody = document.querySelector(PAG_MAP[barId]);
        if(tbody) renderPag(barId, tbody);
    });
}

var PAG_MAP = {
    'pag-items':      '#tab-items tbody',
    'pag-warehouses': '#tab-warehouses tbody',
    'pag-suppliers':  '#tab-suppliers tbody',
    'pag-orders':     '#tab-orders tbody',
    'pag-movements':  '#tab-movements tbody',
    'pag-alerts':     '#tab-alerts tbody',
};
initPagination();
