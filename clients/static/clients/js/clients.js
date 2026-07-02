/* clients.js */
'use strict';

// ── helpers ──────────────────────────────────────────────────────────────────
function openPanel(overlayId, panelId) {
    document.getElementById(overlayId).classList.add('open');
    document.getElementById(panelId).classList.add('open');
    document.body.style.overflow = 'hidden';
}
function closePanel(overlayId, panelId) {
    document.getElementById(overlayId).classList.remove('open');
    document.getElementById(panelId).classList.remove('open');
    document.body.style.overflow = '';
}

// ── type toggle ───────────────────────────────────────────────────────────────
function setType(type) {
    document.getElementById('typeIndividual').checked = (type === 'individual');
    document.getElementById('typeCompany').checked    = (type === 'company');
    document.querySelectorAll('.type-opt').forEach(el => el.classList.remove('active'));
    const active = type === 'individual'
        ? document.getElementById('optIndividual')
        : document.getElementById('optCompany');
    if (active) active.classList.add('active');

    const indFields  = document.getElementById('individualFields');
    const compFields = document.getElementById('companyFields');
    if (indFields)  indFields.style.display  = type === 'individual' ? 'block' : 'none';
    if (compFields) compFields.style.display = type === 'company'    ? 'block' : 'none';

    const isCompany = type === 'company';

    // Email: optional for individual, required for company
    const fEmail = document.getElementById('fEmail');
    const lblEmail = document.getElementById('lblEmail');
    fEmail.required = isCompany;
    if (lblEmail) {
        lblEmail.innerHTML = 'البريد الإلكتروني <span class="' + (isCompany ? 'lbl-req' : 'lbl-opt') + '">' + (isCompany ? 'إلزامي' : 'اختياري') + '</span>';
    }

    // Address: optional for individual, required for company
    const fAddress = document.getElementById('fAddress');
    const lblAddress = document.getElementById('lblAddress');
    fAddress.required = isCompany;
    if (lblAddress) {
        lblAddress.innerHTML = 'العنوان <span class="' + (isCompany ? 'lbl-req' : 'lbl-opt') + '">' + (isCompany ? 'إلزامي' : 'اختياري') + '</span>';
    }

    // Tax number: required for company only (hidden when individual so clear required)
    const fTaxNumber = document.getElementById('fTaxNumber');
    if (fTaxNumber) fTaxNumber.required = isCompany;
}

document.querySelectorAll('.type-opt').forEach(opt => {
    opt.addEventListener('click', () => {
        const radio = opt.querySelector('input[type="radio"]');
        if (radio) setType(radio.value);
    });
});

// ── logo upload preview ───────────────────────────────────────────────────────
function initLogoUpload(inputId, previewId, removeBtnId) {
    const input     = document.getElementById(inputId);
    const preview   = document.getElementById(previewId);
    const removeBtn = document.getElementById(removeBtnId);
    if (!input || !preview || !removeBtn) return;

    input.addEventListener('change', () => {
        const file = input.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = e => {
            preview.src = e.target.result;
            preview.classList.add('visible');
            removeBtn.classList.add('visible');
        };
        reader.readAsDataURL(file);
    });

    removeBtn.addEventListener('click', e => {
        e.stopPropagation();
        input.value = '';
        preview.src = '';
        preview.classList.remove('visible');
        removeBtn.classList.remove('visible');
        document.getElementById('removeLogo').value = '1';
    });
}

initLogoUpload('logoInput', 'logoPreview', 'removeLogo_btn');

// ── add modal ─────────────────────────────────────────────────────────────────
function openAddModal() {
    document.getElementById('panelTitle').textContent = 'إضافة عميل جديد';
    document.getElementById('clientForm').reset();
    document.getElementById('formClientId').value = '';
    document.getElementById('removeLogo').value = '0';
    const preview = document.getElementById('logoPreview');
    preview.classList.remove('visible');
    preview.src = '';
    document.getElementById('removeLogo_btn').classList.remove('visible');
    setType('individual');
    openPanel('panelOverlay', 'clientPanel');
}

// ── edit modal ────────────────────────────────────────────────────────────────
function editClient(id) {
    closeAllMenus();
    fetch(URL_DETAIL.replace('0', id))
        .then(r => r.json())
        .then(data => {
            document.getElementById('panelTitle').textContent = 'تعديل بيانات العميل';
            document.getElementById('formClientId').value = id;
            document.getElementById('fName').value              = data.name || '';
            document.getElementById('fPhone').value             = data.phone || '';
            document.getElementById('fEmail').value             = data.email || '';
            document.getElementById('fAddress').value           = data.address || '';
            document.getElementById('fNotes').value             = data.notes || '';
            document.getElementById('fNationalId').value        = data.national_id || '';
            document.getElementById('fTaxNumber').value         = data.tax_number || '';
            document.getElementById('fCommercial').value        = data.commercial_registration || '';
            document.getElementById('fContactPerson').value     = data.contact_person || '';
            document.getElementById('fContactTitle').value      = data.contact_person_title || '';
            document.getElementById('fWebsite').value           = data.website || '';
            document.getElementById('removeLogo').value = '0';

            const preview   = document.getElementById('logoPreview');
            const removeBtn = document.getElementById('removeLogo_btn');
            if (data.logo_url) {
                preview.src = data.logo_url;
                preview.classList.add('visible');
                removeBtn.classList.add('visible');
            } else {
                preview.src = '';
                preview.classList.remove('visible');
                removeBtn.classList.remove('visible');
            }

            setType(data.client_type || 'individual');
            openPanel('panelOverlay', 'clientPanel');
        });
}

// ── save (add or edit) ────────────────────────────────────────────────────────
document.getElementById('clientForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const id   = document.getElementById('formClientId').value;
    const url  = id ? URL_EDIT.replace('0', id) : URL_CREATE;
    const data = new FormData(this);
    if (!id) data.delete('id');

    fetch(url, { method: 'POST', body: data, headers: { 'X-CSRFToken': CSRF } })
        .then(r => r.json())
        .then(res => {
            if (res.ok) {
                location.reload();
            } else {
                alert('حدث خطأ: ' + (res.error || 'غير معروف'));
            }
        });
});

// ── delete ────────────────────────────────────────────────────────────────────
let pendingDeleteId = null;
function deleteClient(id, name) {
    closeAllMenus();
    pendingDeleteId = id;
    document.getElementById('deleteClientName').textContent = name;
    document.getElementById('deleteOverlay').classList.add('open');
    document.getElementById('deleteModal').classList.add('open');
}

document.getElementById('btnConfirmDelete').addEventListener('click', function() {
    if (!pendingDeleteId) return;
    const url = URL_DELETE.replace('0', pendingDeleteId);
    fetch(url, { method: 'POST', headers: { 'X-CSRFToken': CSRF } })
        .then(r => r.json())
        .then(res => {
            if (res.ok) location.reload();
        });
});

document.getElementById('btnCancelDelete').addEventListener('click', function() {
    document.getElementById('deleteOverlay').classList.remove('open');
    document.getElementById('deleteModal').classList.remove('open');
    pendingDeleteId = null;
});

// ── close panels ──────────────────────────────────────────────────────────────
document.getElementById('panelOverlay').addEventListener('click', () => closePanel('panelOverlay', 'clientPanel'));
document.getElementById('panelCloseBtn').addEventListener('click', () => closePanel('panelOverlay', 'clientPanel'));
document.getElementById('panelCancelBtn').addEventListener('click', () => closePanel('panelOverlay', 'clientPanel'));

document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
        closePanel('panelOverlay', 'clientPanel');
        document.getElementById('deleteOverlay').classList.remove('open');
        document.getElementById('deleteModal').classList.remove('open');
        pendingDeleteId = null;
    }
});

// ── view modal ────────────────────────────────────────────────────────────────
function viewClient(id) {
    closeAllMenus();
    fetch(URL_DETAIL.replace('0', id))
        .then(r => r.json())
        .then(d => {
            document.getElementById('vmAvatar').textContent = (d.name || '؟').charAt(0).toUpperCase();
            document.getElementById('vmName').textContent   = d.name || '';
            var types = {individual:'فرد',company:'شركة',government:'جهة حكومية'};
            document.getElementById('vmType').textContent   = types[d.client_type] || '';

            var fields = [
                ['الهاتف',           d.phone],
                ['البريد الإلكتروني', d.email],
                ['العنوان',           d.address],
                ['الشخص المسؤول',    d.contact_person],
                ['الصفة',            d.contact_person_title],
                ['الهوية / الإقامة', d.national_id],
                ['الرقم الضريبي',    d.tax_number],
                ['السجل التجاري',    d.commercial_registration],
                ['الموقع',           d.website],
            ].filter(function(f){ return f[1]; });

            document.getElementById('vmFields').innerHTML = fields.map(function(f){
                return '<div style="background:var(--earth,#F5F0E8);border-radius:10px;padding:10px 14px">' +
                    '<div style="font-size:11px;font-weight:700;color:var(--text-muted,#8A7A65);margin-bottom:3px">' + f[0] + '</div>' +
                    '<div style="font-size:13px;color:var(--text,#1A1812);font-weight:500">' + f[1] + '</div>' +
                    '</div>';
            }).join('');

            var notesRow = document.getElementById('vmNotesRow');
            if (d.notes) {
                document.getElementById('vmNotes').textContent = d.notes;
                notesRow.style.display = 'flex';
            } else {
                notesRow.style.display = 'none';
            }

            document.getElementById('vmEditBtn').onclick = function(){ closeViewModal(); editClient(id); };

            var overlay = document.getElementById('viewOverlay');
            var modal   = document.getElementById('viewModal');
            overlay.style.opacity = '1'; overlay.style.pointerEvents = 'auto';
            modal.style.opacity = '1'; modal.style.pointerEvents = 'auto';
            modal.style.transform = 'translate(-50%,-50%) scale(1)';
        });
}

function closeViewModal() {
    var overlay = document.getElementById('viewOverlay');
    var modal   = document.getElementById('viewModal');
    overlay.style.opacity = '0'; overlay.style.pointerEvents = 'none';
    modal.style.opacity = '0'; modal.style.pointerEvents = 'none';
    modal.style.transform = 'translate(-50%,-50%) scale(.95)';
}

// ── dropdown menus ────────────────────────────────────────────────────────────
function openMenu(btn, id) {
    closeAllMenus();
    const menu = document.getElementById('menu-' + id);
    if (menu) {
        menu.classList.add('open');
        btn.classList.add('active');
    }
}
function closeAllMenus() {
    document.querySelectorAll('.card-menu.open').forEach(m => m.classList.remove('open'));
}
document.addEventListener('click', e => {
    if (!e.target.closest('.card-menu-btn') && !e.target.closest('.card-menu')) {
        closeAllMenus();
    }
});

// ── search debounce ───────────────────────────────────────────────────────────
const searchInput = document.getElementById('searchInput');
if (searchInput) {
    let timer;
    searchInput.addEventListener('input', () => {
        clearTimeout(timer);
        timer = setTimeout(() => {
            const url = new URL(location.href);
            url.searchParams.set('q', searchInput.value);
            url.searchParams.delete('page');
            location.href = url.toString();
        }, 500);
    });
}

// ── sidebar sync (same as dashboard) ─────────────────────────────────────────
(function() {
    const sidebar = document.getElementById('sidebar');
    const toggle  = document.getElementById('sidebarToggle');
    if (!sidebar) return;

    const STORAGE_KEY = 'sidebar_expanded';
    function setExpanded(expanded) {
        sidebar.classList.toggle('expanded', expanded);
        document.body.classList.toggle('sidebar-open', expanded);
        localStorage.setItem(STORAGE_KEY, expanded ? '1' : '0');
    }

    setExpanded(localStorage.getItem(STORAGE_KEY) === '1');

    if (toggle) {
        toggle.addEventListener('click', () => {
            setExpanded(!sidebar.classList.contains('expanded'));
        });
    }

    document.addEventListener('keydown', e => {
        if ((e.key === '[' || e.key === 'b' || e.key === 'B') && !e.target.matches('input,textarea')) {
            setExpanded(!sidebar.classList.contains('expanded'));
        }
    });
})();
