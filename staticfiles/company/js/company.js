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

/* ── logo preview ── */
var logoInput = document.getElementById('logoInput');
if(logoInput){
    logoInput.addEventListener('change', function(){
        var file = this.files[0];
        if(!file) return;
        var reader = new FileReader();
        reader.onload = function(e){
            var img = document.getElementById('logoPreview');
            if(img){ img.src = e.target.result; img.style.display = ''; }
        };
        reader.readAsDataURL(file);
    });
}

/* ── doc delete ── */
function deleteDoc(url, name){
    if(!confirm('حذف "' + name + '"؟')) return;
    fetch(url, {
        method: 'POST',
        headers: {'X-CSRFToken': CSRF, 'Content-Type': 'application/json'},
        body: '{}'
    }).then(function(r){ return r.json(); }).then(function(d){
        if(d.ok) location.reload();
        else alert('خطأ في الحذف');
    });
}

/* ── doc upload panel ── */
function openDocPanel(){
    document.getElementById('docOverlay').classList.add('active');
    document.getElementById('docPanel').classList.add('active');
}
function closeDocPanel(){
    document.getElementById('docOverlay').classList.remove('active');
    document.getElementById('docPanel').classList.remove('active');
}
var docOverlay = document.getElementById('docOverlay');
if(docOverlay) docOverlay.addEventListener('click', closeDocPanel);

/* ── payment methods panel ── */
var _pmEditPk = null;

function openPmPanel(){
    _pmEditPk = null;
    document.getElementById('pmPanelTitle').textContent = 'إضافة طريقة دفع';
    document.getElementById('pmName').value      = '';
    document.getElementById('pmType').value      = 'immediate';
    document.getElementById('pmCompany').value   = '';
    document.getElementById('pmFeePerc').value   = '0';
    document.getElementById('pmFixedFee').value  = '0';
    document.getElementById('pmNotes').value     = '';
    document.getElementById('pmOverlay').classList.add('active');
    document.getElementById('pmPanel').classList.add('active');
}

function editPm(pk, name, type, company, feePerc, fixedFee, notes){
    _pmEditPk = pk;
    document.getElementById('pmPanelTitle').textContent = 'تعديل طريقة الدفع';
    document.getElementById('pmName').value      = name;
    document.getElementById('pmType').value      = type;
    document.getElementById('pmCompany').value   = company;
    document.getElementById('pmFeePerc').value   = feePerc;
    document.getElementById('pmFixedFee').value  = fixedFee;
    document.getElementById('pmNotes').value     = notes;
    document.getElementById('pmOverlay').classList.add('active');
    document.getElementById('pmPanel').classList.add('active');
}

function closePmPanel(){
    document.getElementById('pmOverlay').classList.remove('active');
    document.getElementById('pmPanel').classList.remove('active');
}

function submitPm(){
    var name = document.getElementById('pmName').value.trim();
    if(!name){ alert('يرجى إدخال اسم طريقة الدفع'); return; }
    var url = _pmEditPk ? '/company/pm/' + _pmEditPk + '/edit/' : '/company/pm/create/';
    fetch(url, {
        method: 'POST',
        headers: {'X-CSRFToken': CSRF, 'Content-Type': 'application/json'},
        body: JSON.stringify({
            name:           name,
            payment_type:   document.getElementById('pmType').value,
            company_name:   document.getElementById('pmCompany').value.trim(),
            fee_percentage: parseFloat(document.getElementById('pmFeePerc').value) || 0,
            fixed_fee:      parseFloat(document.getElementById('pmFixedFee').value) || 0,
            notes:          document.getElementById('pmNotes').value.trim(),
        })
    }).then(function(r){ return r.json(); }).then(function(d){
        if(d.ok){ closePmPanel(); location.reload(); }
        else alert('خطأ: ' + (d.error || ''));
    });
}

function deletePm(pk, name){
    if(!confirm('حذف طريقة الدفع "' + name + '"؟')) return;
    fetch('/company/pm/' + pk + '/delete/', {
        method: 'POST',
        headers: {'X-CSRFToken': CSRF, 'Content-Type': 'application/json'},
        body: '{}'
    }).then(function(r){ return r.json(); }).then(function(d){
        if(d.ok) location.reload();
        else alert('خطأ في الحذف');
    });
}
