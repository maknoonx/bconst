/* ══════════════════════════════
   accounting.js
══════════════════════════════ */

/* ── sidebar ── */
(function() {
    const sidebar = document.getElementById('sidebar');
    const btn     = document.getElementById('sidebarToggle');
    const KEY     = 'sidebar_expanded';
    if (!sidebar || !btn) return;
    function setExpanded(val) {
        sidebar.classList.toggle('expanded', val);
        document.body.classList.toggle('sidebar-open', val);
        localStorage.setItem(KEY, val ? '1' : '0');
    }
    const saved = localStorage.getItem(KEY);
    setExpanded(saved === '1' || saved === 'true');
    btn.addEventListener('click', () => setExpanded(!sidebar.classList.contains('expanded')));
})();

/* ── tabs ── */
document.querySelectorAll('.acc-tab').forEach(tab => {
    tab.addEventListener('click', function() {
        document.querySelectorAll('.acc-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.acc-section').forEach(s => s.classList.remove('active'));
        this.classList.add('active');
        document.getElementById('tab-' + this.dataset.tab).classList.add('active');
    });
});

/* ── modal helpers ── */
function openModal(ovId, panId) {
    document.getElementById(ovId).classList.add('active');
    document.getElementById(panId).classList.add('active');
    document.body.style.overflow = 'hidden';
}
function closeModal(ovId, panId) {
    document.getElementById(ovId).classList.remove('active');
    document.getElementById(panId).classList.remove('active');
    document.body.style.overflow = '';
}

/* ── number formatting ── */
function fmt(n) {
    return parseFloat(n || 0).toLocaleString('ar-SA', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

/* ════════════════════════
   ACCOUNTS
════════════════════════ */
function openAddAccount() {
    document.getElementById('accForm').reset();
    document.getElementById('editAccId').value = '';
    document.getElementById('accModalTitle').textContent = 'حساب جديد';
    openModal('accOverlay', 'accPanel');
}

function editAccount(id, code, name, typeId, parentId, notes) {
    document.getElementById('editAccId').value  = id;
    document.getElementById('aCode').value      = code;
    document.getElementById('aName').value      = name;
    document.getElementById('aType').value      = typeId;
    document.getElementById('aParent').value    = parentId || '';
    document.getElementById('aNotes').value     = notes;
    document.getElementById('accModalTitle').textContent = 'تعديل الحساب';
    openModal('accOverlay', 'accPanel');
}

function submitAccount() {
    const id = document.getElementById('editAccId').value;
    const url = id ? `/accounting/accounts/${id}/edit/` : URL_ACC_CREATE;
    const fd  = new FormData(document.getElementById('accForm'));
    fetch(url, { method: 'POST', body: fd })
        .then(r => r.json())
        .then(d => { if (d.ok) location.reload(); else alert(d.error || 'حدث خطأ'); });
}

function deleteAccount(id, name) {
    setPending(`/accounting/accounts/${id}/delete/`, name);
}

function closeAccModal() { closeModal('accOverlay', 'accPanel'); }

/* ════════════════════════
   JOURNALS
════════════════════════ */
let lineCount = 0;

function openAddJournal() {
    document.getElementById('journalForm').reset();
    document.getElementById('jLinesBody').innerHTML = '';
    lineCount = 0;
    addJournalLine(); addJournalLine(); // start with 2 lines
    updateJournalTotals();
    document.getElementById('jModalTitle').textContent = 'قيد يومية جديد';
    openModal('jOverlay', 'jPanel');
}

function addJournalLine() {
    lineCount++;
    const tr = document.createElement('tr');
    tr.id = `jline-${lineCount}`;
    tr.innerHTML = `
        <td>
            <select name="line_account[]" class="jl-account" onchange="updateJournalTotals()" required>
                <option value="">اختر حساباً...</option>
                ${ACCOUNTS_OPTIONS}
            </select>
        </td>
        <td><input type="number" name="line_debit[]"  class="jl-debit"  min="0" step="0.01" value="0" oninput="updateJournalTotals()"></td>
        <td><input type="number" name="line_credit[]" class="jl-credit" min="0" step="0.01" value="0" oninput="updateJournalTotals()"></td>
        <td><input type="text"   name="line_note[]"   placeholder="ملاحظة"></td>
        <td style="text-align:center">
            <button type="button" onclick="removeJLine(${lineCount})" style="background:none;border:none;cursor:pointer;color:#ef4444;font-size:16px">✕</button>
        </td>`;
    document.getElementById('jLinesBody').appendChild(tr);
}

function removeJLine(n) {
    const row = document.getElementById(`jline-${n}`);
    if (row) row.remove();
    updateJournalTotals();
}

function updateJournalTotals() {
    let totalDebit = 0, totalCredit = 0;
    document.querySelectorAll('.jl-debit').forEach(i => totalDebit += parseFloat(i.value || 0));
    document.querySelectorAll('.jl-credit').forEach(i => totalCredit += parseFloat(i.value || 0));
    const balanced = Math.abs(totalDebit - totalCredit) < 0.01;
    document.getElementById('jTotalDebit').textContent  = fmt(totalDebit);
    document.getElementById('jTotalCredit').textContent = fmt(totalCredit);
    const status = document.getElementById('jBalanceStatus');
    status.textContent = balanced ? '✓ متوازن' : '✗ غير متوازن';
    status.className   = balanced ? 'j-balanced' : 'j-unbalanced';
}

function submitJournal() {
    const fd  = new FormData(document.getElementById('journalForm'));
    fetch(URL_JOURNAL_CREATE, { method: 'POST', body: fd })
        .then(r => r.json())
        .then(d => {
            if (d.ok) {
                if (!d.balanced) alert('تحذير: القيد غير متوازن — تم الحفظ كمسودة');
                location.reload();
            } else {
                alert(d.error || 'حدث خطأ');
            }
        });
}

function postJournal(id) {
    const fd = new FormData();
    fd.append('csrfmiddlewaretoken', CSRF);
    fetch(`/accounting/journals/${id}/post/`, { method: 'POST', body: fd })
        .then(r => r.json())
        .then(d => {
            if (d.ok) location.reload();
            else alert(d.error || 'القيد غير متوازن، لا يمكن اعتماده');
        });
}

function viewJournal(id) {
    fetch(`/accounting/journals/${id}/`)
        .then(r => r.json())
        .then(d => {
            let html = `<div style="margin-bottom:16px"><strong>${d.number}</strong> — ${d.date}<br><span style="color:var(--text-muted)">${d.description}</span></div>`;
            html += `<table class="j-lines" style="width:100%"><thead><tr><th>الحساب</th><th>مدين</th><th>دائن</th><th>ملاحظة</th></tr></thead><tbody>`;
            d.lines.forEach(l => {
                html += `<tr><td>${l.account_name}</td><td style="color:#22c55e">${parseFloat(l.debit) > 0 ? fmt(l.debit) : ''}</td><td style="color:#ef4444">${parseFloat(l.credit) > 0 ? fmt(l.credit) : ''}</td><td>${l.note}</td></tr>`;
            });
            html += `</tbody><tfoot><tr><td>الإجمالي</td><td>${fmt(d.total_debit)}</td><td>${fmt(d.total_credit)}</td><td></td></tr></tfoot></table>`;
            document.getElementById('jViewBody').innerHTML = html;
            openModal('jViewOverlay', 'jViewPanel');
        });
}

function deleteJournal(id, name) { setPending(`/accounting/journals/${id}/delete/`, name); }
function closeJModal()     { closeModal('jOverlay', 'jPanel'); }
function closeJViewModal() { closeModal('jViewOverlay', 'jViewPanel'); }

/* ════════════════════════
   ASSETS
════════════════════════ */
function openAddAsset() {
    document.getElementById('assetForm').reset();
    document.getElementById('editAssetId').value = '';
    document.getElementById('assetModalTitle').textContent = 'أصل ثابت جديد';
    openModal('assetOverlay', 'assetPanel');
}

function editAsset(id, name, category, purchaseDate, cost, life, salvage, notes) {
    document.getElementById('editAssetId').value   = id;
    document.getElementById('asName').value        = name;
    document.getElementById('asCategory').value    = category;
    document.getElementById('asPurchaseDate').value = purchaseDate;
    document.getElementById('asCost').value        = cost;
    document.getElementById('asLife').value        = life;
    document.getElementById('asSalvage').value     = salvage;
    document.getElementById('asNotes').value       = notes;
    document.getElementById('assetModalTitle').textContent = 'تعديل الأصل';
    openModal('assetOverlay', 'assetPanel');
}

function submitAsset() {
    const id  = document.getElementById('editAssetId').value;
    const url = id ? `/accounting/assets/${id}/edit/` : URL_ASSET_CREATE;
    const fd  = new FormData(document.getElementById('assetForm'));
    fetch(url, { method: 'POST', body: fd })
        .then(r => r.json())
        .then(d => { if (d.ok) location.reload(); else alert(d.error || 'حدث خطأ'); });
}

function deleteAsset(id, name) { setPending(`/accounting/assets/${id}/delete/`, name); }
function closeAssetModal() { closeModal('assetOverlay', 'assetPanel'); }

/* ════════════════════════
   PAYROLL
════════════════════════ */
function openAddPayroll() {
    document.getElementById('payrollForm').reset();
    // rebuild lines from employees
    const tbody = document.getElementById('prLinesBody');
    tbody.innerHTML = '';
    EMPLOYEES.forEach(emp => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><input type="hidden" name="employee_id[]" value="${emp.id}">${emp.name}</td>
            <td><input type="number" name="basic[]"       min="0" step="0.01" value="0" class="pr-basic"></td>
            <td><input type="number" name="allowances[]"  min="0" step="0.01" value="0"></td>
            <td><input type="number" name="deductions[]"  min="0" step="0.01" value="0"></td>
            <td><input type="text"   name="deduction_note[]" placeholder="السبب"></td>
            <td><input type="number" name="bonus[]"       min="0" step="0.01" value="0"></td>
            <td><input type="text"   name="bonus_note[]"  placeholder="السبب"></td>`;
        tbody.appendChild(tr);
    });
    openModal('payrollOverlay', 'payrollPanel');
}

function viewPayroll(id) {
    fetch(`/accounting/payrolls/${id}/`)
        .then(r => r.json())
        .then(d => {
            let html = `<div style="margin-bottom:16px;font-size:13px;color:var(--text-muted)">${d.period} — إجمالي: <strong>${fmt(d.total_gross)}</strong> ﷼ | صافي: <strong>${fmt(d.total_net)}</strong> ﷼</div>`;
            html += `<table style="width:100%;border-collapse:collapse;font-size:12px"><thead><tr style="background:var(--earth)">
                <th style="padding:8px;text-align:right;border:1px solid var(--earth-2)">الموظف</th>
                <th style="padding:8px;border:1px solid var(--earth-2)">أساسي</th>
                <th style="padding:8px;border:1px solid var(--earth-2)">بدلات</th>
                <th style="padding:8px;border:1px solid var(--earth-2)">استقطاع</th>
                <th style="padding:8px;border:1px solid var(--earth-2)">بونص</th>
                <th style="padding:8px;border:1px solid var(--earth-2)">صافي</th>
            </tr></thead><tbody>`;
            d.lines.forEach(l => {
                html += `<tr><td style="padding:7px 8px;border:1px solid var(--earth-2)">${l.employee}</td>
                    <td style="padding:7px 8px;border:1px solid var(--earth-2);text-align:center">${fmt(l.basic)}</td>
                    <td style="padding:7px 8px;border:1px solid var(--earth-2);text-align:center">${fmt(l.allowances)}</td>
                    <td style="padding:7px 8px;border:1px solid var(--earth-2);text-align:center;color:#ef4444">${parseFloat(l.deductions)>0?fmt(l.deductions):''}</td>
                    <td style="padding:7px 8px;border:1px solid var(--earth-2);text-align:center;color:#22c55e">${parseFloat(l.bonus)>0?fmt(l.bonus):''}</td>
                    <td style="padding:7px 8px;border:1px solid var(--earth-2);font-weight:700">${fmt(l.net)}</td></tr>`;
            });
            html += '</tbody></table>';
            document.getElementById('prViewBody').innerHTML = html;
            openModal('prViewOverlay', 'prViewPanel');
        });
}

function postPayroll(id) {
    const fd = new FormData();
    fd.append('csrfmiddlewaretoken', CSRF);
    fetch(`/accounting/payrolls/${id}/post/`, { method: 'POST', body: fd })
        .then(r => r.json())
        .then(d => { if (d.ok) location.reload(); else alert(d.error || 'حدث خطأ'); });
}

function submitPayroll() {
    const fd = new FormData(document.getElementById('payrollForm'));
    fetch(URL_PAYROLL_CREATE, { method: 'POST', body: fd })
        .then(r => r.json())
        .then(d => { if (d.ok) location.reload(); else alert(d.error || 'حدث خطأ'); });
}

function closePayrollModal()     { closeModal('payrollOverlay', 'payrollPanel'); }
function closePrViewModal()      { closeModal('prViewOverlay', 'prViewPanel'); }

/* ════════════════════════
   PERIODS
════════════════════════ */
function togglePeriod(id) {
    const fd = new FormData();
    fd.append('csrfmiddlewaretoken', CSRF);
    fetch(`/accounting/periods/${id}/toggle/`, { method: 'POST', body: fd })
        .then(r => r.json())
        .then(d => { if (d.ok) location.reload(); });
}

function openAddPeriod() { openModal('periodOverlay', 'periodPanel'); }
function closePeriodModal() { closeModal('periodOverlay', 'periodPanel'); }

function submitPeriod() {
    const fd = new FormData(document.getElementById('periodForm'));
    fetch(URL_PERIOD_CREATE, { method: 'POST', body: fd })
        .then(r => r.json())
        .then(d => { if (d.ok) location.reload(); else alert(d.error || 'حدث خطأ'); });
}

/* ════════════════════════
   DELETE confirm
════════════════════════ */
let pendingDeleteUrl = null;
function setPending(url, name) {
    pendingDeleteUrl = url;
    document.getElementById('delName').textContent = name;
    document.getElementById('delOverlay').classList.add('active');
    document.getElementById('delModal').classList.add('active');
    document.body.style.overflow = 'hidden';
}
document.getElementById('delConfirmBtn').onclick = function() {
    if (!pendingDeleteUrl) return;
    const fd = new FormData();
    fd.append('csrfmiddlewaretoken', CSRF);
    fetch(pendingDeleteUrl, { method: 'POST', body: fd })
        .then(r => r.json())
        .then(d => { if (d.ok) location.reload(); });
};
document.getElementById('delCancelBtn').onclick = () => {
    document.getElementById('delOverlay').classList.remove('active');
    document.getElementById('delModal').classList.remove('active');
    document.body.style.overflow = '';
};
document.getElementById('delOverlay').onclick = () => {
    document.getElementById('delOverlay').classList.remove('active');
    document.getElementById('delModal').classList.remove('active');
    document.body.style.overflow = '';
};

/* ── ESC ── */
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
        ['accOverlay','jOverlay','jViewOverlay','assetOverlay','payrollOverlay','prViewOverlay','periodOverlay'].forEach(ov => {
            const el = document.getElementById(ov);
            if (el && el.classList.contains('active')) {
                const pan = ov.replace('Overlay', 'Panel');
                closeModal(ov, pan);
            }
        });
        document.getElementById('delOverlay').classList.remove('active');
        document.getElementById('delModal').classList.remove('active');
        document.body.style.overflow = '';
    }
});

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
    'pag-accounts': '#tab-accounts tbody',
    'pag-journals': '#tab-journals tbody',
    'pag-payroll':  '#tab-payroll tbody',
    'pag-assets':   '#tab-assets tbody',
    'pag-periods':  '#tab-periods tbody',
};
initPagination();
