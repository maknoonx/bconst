/* marketing.js */
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
document.querySelectorAll('.mkt-tab').forEach(function(tab){
    tab.addEventListener('click', function(){
        document.querySelectorAll('.mkt-tab').forEach(function(t){ t.classList.remove('active'); });
        document.querySelectorAll('.mkt-section').forEach(function(s){ s.classList.remove('active'); });
        tab.classList.add('active');
        var sec = document.getElementById('tab-' + tab.dataset.tab);
        if(sec) sec.classList.add('active');
    });
});

/* ── live search ── */
document.querySelectorAll('.mkt-search').forEach(function(input){
    input.addEventListener('input', function(){
        var q = input.value.trim().toLowerCase();
        var tbody = document.querySelector('#tab-' + input.dataset.target + ' tbody');
        if(!tbody) return;
        tbody.querySelectorAll('tr').forEach(function(row){
            row.style.display = q && !row.textContent.toLowerCase().includes(q) ? 'none' : '';
        });
    });
});

/* ── helpers ── */
function post(url, data){
    return fetch(url, {
        method: 'POST',
        headers: {'Content-Type':'application/json','X-CSRFToken':CSRF},
        body: JSON.stringify(data)
    }).then(function(r){ return r.json(); });
}
function showErr(msg){ alert('خطأ: ' + msg); }
function openPanel(ovId, panId){
    document.getElementById(ovId).classList.add('active');
    document.getElementById(panId).classList.add('active');
}
function closePanel(ovId, panId){
    document.getElementById(ovId).classList.remove('active');
    document.getElementById(panId).classList.remove('active');
}

/* ── delete confirm ── */
var _delUrl = '', _delCb = null;
function setPending(url, name, cb){
    _delUrl = url; _delCb = cb || null;
    document.getElementById('delName').textContent = name;
    document.getElementById('mktDelOverlay').classList.add('active');
    document.getElementById('mktDelModal').classList.add('active');
}
function closeDel(){
    document.getElementById('mktDelOverlay').classList.remove('active');
    document.getElementById('mktDelModal').classList.remove('active');
}
document.getElementById('delCancelBtn').addEventListener('click', closeDel);
document.getElementById('delConfirmBtn').addEventListener('click', function(){
    post(_delUrl, {}).then(function(r){
        if(r.ok){ closeDel(); location.reload(); }
        else showErr(r.error);
    });
});

/* ════════════════════════════════
   PLANS data & state
════════════════════════════════ */
var PLANS = window.PLANS_DATA || [];
var _editPlanId = null;

/* ── sub-list builders ── */
function buildObjectivesRows(items){
    var tbody = document.getElementById('objBody');
    tbody.innerHTML = '';
    (items || []).forEach(function(o){ addObjectiveRow(o.title, o.goal); });
}
function addObjectiveRow(title, goal){
    var tr = document.createElement('tr');
    tr.innerHTML =
        '<td><input type="text" class="obj-title-in" placeholder="العنوان" value="' + esc(title||'') + '"></td>' +
        '<td><input type="text" class="obj-goal-in" placeholder="الهدف" value="' + esc(goal||'') + '"></td>' +
        '<td><button type="button" class="rm-btn" onclick="this.closest(\'tr\').remove()">×</button></td>';
    document.getElementById('objBody').appendChild(tr);
}

function buildBudgetRows(items){
    var tbody = document.getElementById('budBody');
    tbody.innerHTML = '';
    (items || []).forEach(function(b){ addBudgetRow(b.type, b.amount); });
}
function addBudgetRow(type, amount){
    var tr = document.createElement('tr');
    tr.innerHTML =
        '<td><input type="text" class="bud-type-in" placeholder="نوع الميزانية" value="' + esc(type||'') + '"></td>' +
        '<td><input type="number" class="bud-amount-in" placeholder="0" step="0.01" min="0" value="' + (amount||'') + '"></td>' +
        '<td><button type="button" class="rm-btn" onclick="this.closest(\'tr\').remove()">×</button></td>';
    document.getElementById('budBody').appendChild(tr);
}

function buildChannelRows(items){
    var tbody = document.getElementById('chBody');
    tbody.innerHTML = '';
    (items || []).forEach(function(ch){ addChannelRow(ch.name); });
}
function addChannelRow(name){
    var tr = document.createElement('tr');
    tr.innerHTML =
        '<td><input type="text" class="ch-name-in" placeholder="اسم القناة" value="' + esc(name||'') + '"></td>' +
        '<td><button type="button" class="rm-btn" onclick="this.closest(\'tr\').remove()">×</button></td>';
    document.getElementById('chBody').appendChild(tr);
}

function buildTargetRows(items){
    var tbody = document.getElementById('tgtBody');
    tbody.innerHTML = '';
    (items || []).forEach(function(t){ addTargetRow(t.target_type, t.label, t.target_value); });
}
function addTargetRow(type, label, value){
    var tr = document.createElement('tr');
    tr.innerHTML =
        '<td><select class="tgt-type-in">' +
            '<option value="revenue"' + (type==='revenue'?' selected':'') + '>إيرادات</option>' +
            '<option value="contracts"' + (type==='contracts'?' selected':'') + '>عقود</option>' +
            '<option value="leads"' + (type==='leads'?' selected':'') + '>عملاء محتملون</option>' +
            '<option value="projects"' + (type==='projects'?' selected':'') + '>مشاريع</option>' +
            '<option value="general"' + (type==='general'?' selected':'') + '>عام</option>' +
        '</select></td>' +
        '<td><input type="text" class="tgt-label-in" placeholder="الوصف" value="' + esc(label||'') + '"></td>' +
        '<td><input type="number" class="tgt-value-in" placeholder="0" step="0.01" min="0" value="' + (value||'') + '"></td>' +
        '<td><button type="button" class="rm-btn" onclick="this.closest(\'tr\').remove()">×</button></td>';
    document.getElementById('tgtBody').appendChild(tr);
}

function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;'); }

function collectPlanData(){
    var objectives = [];
    document.querySelectorAll('#objBody tr').forEach(function(tr){
        var t = tr.querySelector('.obj-title-in').value.trim();
        if(t) objectives.push({title:t, goal: tr.querySelector('.obj-goal-in').value.trim()});
    });
    var budgets = [];
    document.querySelectorAll('#budBody tr').forEach(function(tr){
        var t = tr.querySelector('.bud-type-in').value.trim();
        if(t) budgets.push({type:t, amount: parseFloat(tr.querySelector('.bud-amount-in').value)||0});
    });
    var channels = [];
    document.querySelectorAll('#chBody tr').forEach(function(tr){
        var n = tr.querySelector('.ch-name-in').value.trim();
        if(n) channels.push({name:n, days:[]});
    });
    var targets = [];
    document.querySelectorAll('#tgtBody tr').forEach(function(tr){
        targets.push({
            target_type:  tr.querySelector('.tgt-type-in').value,
            label:        tr.querySelector('.tgt-label-in').value.trim(),
            target_value: parseFloat(tr.querySelector('.tgt-value-in').value)||0,
        });
    });
    return {objectives:objectives, budgets:budgets, channels:channels, targets:targets};
}

/* ── open plan form ── */
function openAddPlan(){
    _editPlanId = null;
    document.getElementById('planModalTitle').textContent = 'خطة جديدة';
    document.getElementById('planTitle').value = '';
    document.getElementById('planMonth').value = '';
    document.getElementById('planNotes').value = '';
    buildObjectivesRows([]); buildBudgetRows([]); buildChannelRows([]); buildTargetRows([]);
    openPanel('planOverlay','planPanel');
}
function closePlanModal(){ closePanel('planOverlay','planPanel'); }
document.getElementById('planOverlay').addEventListener('click', closePlanModal);

function editPlan(id){
    var p = PLANS.find(function(x){ return x.pk === id; });
    if(!p) return;
    _editPlanId = id;
    document.getElementById('planModalTitle').textContent = 'تعديل الخطة';
    document.getElementById('planTitle').value  = p.title;
    document.getElementById('planMonth').value  = p.month_raw;
    document.getElementById('planNotes').value  = p.notes;
    buildObjectivesRows(p.objectives);
    buildBudgetRows(p.budgets);
    buildChannelRows(p.channels);
    buildTargetRows(p.targets);
    openPanel('planOverlay','planPanel');
}

function submitPlan(){
    var title = document.getElementById('planTitle').value.trim();
    var month = document.getElementById('planMonth').value;
    if(!title) return showErr('عنوان الخطة مطلوب');
    if(!month)  return showErr('الشهر مطلوب');
    var sub = collectPlanData();
    sub.title = title; sub.month = month;
    sub.notes = document.getElementById('planNotes').value.trim();
    var url = _editPlanId ? URL_PLAN_EDIT.replace('0', _editPlanId) : URL_PLAN_CREATE;
    post(url, sub).then(function(r){
        if(r.ok) location.reload();
        else showErr(r.error);
    });
}

/* ── view plan ── */
function viewPlan(id){
    var p = PLANS.find(function(x){ return x.pk === id; });
    if(!p) return;
    var html = '<div class="view-meta">' +
        '<div class="view-meta-item"><div class="lbl">العنوان</div><div class="val">' + esc(p.title) + '</div></div>' +
        '<div class="view-meta-item"><div class="lbl">الشهر</div><div class="val">' + p.month + '</div></div>' +
        '<div class="view-meta-item"><div class="lbl">الحالة</div><div class="val">' + p.status_label + '</div></div>' +
        '<div class="view-meta-item"><div class="lbl">إجمالي الميزانية (ريال)</div><div class="val" style="color:var(--gold)">' + p.total_budget.toFixed(2) + '</div></div>' +
    '</div>';
    if(p.objectives.length){
        html += '<div class="view-section"><h3>الأهداف</h3><ul class="obj-list">';
        p.objectives.forEach(function(o){
            html += '<li class="obj-item"><div class="obj-title">' + esc(o.title) + '</div><div class="obj-sub">' + esc(o.goal) + '</div>';
            if(o.result) html += '<div class="obj-sub" style="color:var(--green)">النتيجة: ' + esc(o.result) + '</div>';
            html += '</li>';
        });
        html += '</ul></div>';
    }
    if(p.budgets.length){
        html += '<div class="view-section"><h3>الميزانية</h3><table class="mkt-table" style="margin:0"><thead><tr><th>البند</th><th>المبلغ (ريال)</th></tr></thead><tbody>';
        p.budgets.forEach(function(b){
            html += '<tr><td>' + esc(b.type) + '</td><td style="font-weight:700;color:var(--gold)">' + b.amount.toFixed(2) + '</td></tr>';
        });
        html += '</tbody></table></div>';
    }
    if(p.targets.length){
        html += '<div class="view-section"><h3>المستهدفات</h3><table class="mkt-table" style="margin:0"><thead><tr><th>النوع</th><th>الوصف</th><th>المستهدف</th><th>النتيجة</th></tr></thead><tbody>';
        var typeMap = {revenue:'إيرادات',contracts:'عقود',leads:'عملاء محتملون',projects:'مشاريع',general:'عام'};
        p.targets.forEach(function(t){
            html += '<tr><td>' + (typeMap[t.target_type]||t.target_type) + '</td><td>' + esc(t.label) + '</td><td>' + t.target_value.toFixed(2) + '</td><td>' + (t.result_value !== null ? t.result_value.toFixed(2) : '—') + '</td></tr>';
        });
        html += '</tbody></table></div>';
    }
    if(p.channels.length){
        html += '<div class="view-section"><h3>قنوات التسويق</h3><ul class="obj-list">';
        p.channels.forEach(function(ch){ html += '<li class="obj-item"><div class="obj-title">' + esc(ch.name) + '</div></li>'; });
        html += '</ul></div>';
    }
    if(p.notes) html += '<div class="view-section"><h3>ملاحظات</h3><p style="font-size:13px;color:var(--text-muted)">' + esc(p.notes) + '</p></div>';
    document.getElementById('planViewBody').innerHTML = html;
    openPanel('planViewOverlay','planViewPanel');
}
function closePlanView(){ closePanel('planViewOverlay','planViewPanel'); }
document.getElementById('planViewOverlay').addEventListener('click', closePlanView);

function approvePlan(id, title){
    if(!confirm('اعتماد الخطة "' + title + '"؟')) return;
    post(URL_PLAN_APPROVE.replace('0', id), {}).then(function(r){
        if(r.ok) location.reload(); else showErr(r.error);
    });
}
function completePlan(id, title){
    if(!confirm('تحديد الخطة "' + title + '" كمكتملة؟')) return;
    post(URL_PLAN_COMPLETE.replace('0', id), {}).then(function(r){
        if(r.ok) location.reload(); else showErr(r.error);
    });
}

/* ════════════════════════════════
   MARKETERS
════════════════════════════════ */
var _editMktId = null;

function openAddMarketer(){
    _editMktId = null;
    document.getElementById('mktModalTitle').textContent = 'مسوق جديد';
    document.getElementById('mktForm').reset();
    openPanel('mktOverlay','mktPanel');
}
function closeMktModal(){ closePanel('mktOverlay','mktPanel'); }
document.getElementById('mktOverlay').addEventListener('click', closeMktModal);

function editMarketer(id, name, phone, email, bank, iban, rate, schedule, notes){
    _editMktId = id;
    document.getElementById('mktModalTitle').textContent = 'تعديل المسوق';
    document.getElementById('mName').value       = name;
    document.getElementById('mPhone').value      = phone;
    document.getElementById('mEmail').value      = email;
    document.getElementById('mBank').value       = bank;
    document.getElementById('mIban').value       = iban;
    document.getElementById('mRate').value       = rate;
    document.getElementById('mSchedule').value   = schedule;
    document.getElementById('mNotes').value      = notes;
    openPanel('mktOverlay','mktPanel');
}

function submitMarketer(){
    var name = document.getElementById('mName').value.trim();
    if(!name) return showErr('اسم المسوق مطلوب');
    var url = _editMktId ? URL_MKT_EDIT.replace('0', _editMktId) : URL_MKT_CREATE;
    post(url, {
        name:                name,
        phone:               document.getElementById('mPhone').value.trim(),
        email:               document.getElementById('mEmail').value.trim(),
        bank:                document.getElementById('mBank').value.trim(),
        iban:                document.getElementById('mIban').value.trim(),
        commission_rate:     parseFloat(document.getElementById('mRate').value)||0,
        settlement_schedule: document.getElementById('mSchedule').value,
        notes:               document.getElementById('mNotes').value.trim(),
    }).then(function(r){
        if(r.ok) location.reload(); else showErr(r.error);
    });
}
