/* ══════════════════════════════
   projects.js
══════════════════════════════ */

/* ── helpers ── */
function openModal(overlayId, panelId) {
    document.getElementById(overlayId).classList.add('active');
    document.getElementById(panelId).classList.add('active');
    document.body.style.overflow = 'hidden';
}
function closeModal(overlayId, panelId) {
    document.getElementById(overlayId).classList.remove('active');
    document.getElementById(panelId).classList.remove('active');
    document.body.style.overflow = '';
}
function resetProjectForm() {
    document.getElementById('projectForm').reset();
    document.getElementById('editId').value = '';
    document.getElementById('progressVal').textContent = '0';
    document.getElementById('modalTitle').textContent = 'مشروع جديد';
    document.getElementById('fClient').value = '';
    document.getElementById('clientPickerLabel').textContent = 'اختر عميلاً...';
    document.getElementById('clientPickerBtn').classList.remove('has-value');
}

/* ── open add modal ── */
function openAddModal() {
    resetProjectForm();
    openModal('modalOverlay', 'modalPanel');
}

document.getElementById('btnAddProject').onclick = openAddModal;
const btnEmpty = document.getElementById('btnAddProjectEmpty');
if (btnEmpty) btnEmpty.onclick = openAddModal;

/* ── close modal ── */
document.getElementById('modalClose').onclick   = () => { closeModal('modalOverlay','modalPanel'); };
document.getElementById('modalCancel').onclick  = () => { closeModal('modalOverlay','modalPanel'); };
document.getElementById('modalOverlay').onclick = () => { closeModal('modalOverlay','modalPanel'); };

/* ── progress slider label ── */
document.getElementById('fProgress').addEventListener('input', function() {
    document.getElementById('progressVal').textContent = this.value;
});

/* ── SUBMIT: create or update ── */
document.getElementById('projectForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const id  = document.getElementById('editId').value;
    const url = id ? getEditUrl(id) : URL_CREATE;
    const fd  = new FormData(this);
    fetch(url, { method: 'POST', body: fd })
        .then(r => r.json())
        .then(d => {
            if (d.ok) window.location.href = URL_LIST;
        });
});

/* ── EDIT ── */
function editProject(id) {
    closeAllMenus();
    fetch(getEditUrl(id))
        .then(r => r.json())
        .then(d => {
            document.getElementById('editId').value      = d.id;
            document.getElementById('fName').value       = d.name;
            document.getElementById('fClient').value     = d.client;
            /* update picker label */
            const lbl = document.getElementById('clientPickerLabel');
            if (d.client) {
                lbl.textContent = d.client;
                document.getElementById('clientPickerBtn').classList.add('has-value');
            } else {
                lbl.textContent = 'اختر عميلاً...';
                document.getElementById('clientPickerBtn').classList.remove('has-value');
            }
            document.getElementById('fLocation').value   = d.location;
            document.getElementById('fDesc').value       = d.description;
            document.getElementById('fStatus').value     = d.status;
            document.getElementById('fBudget').value     = d.budget;
            document.getElementById('fSpent').value      = d.spent;
            document.getElementById('fStart').value      = d.start_date;
            document.getElementById('fEnd').value        = d.end_date;
            document.getElementById('fManager').value    = d.manager;
            document.getElementById('fProgress').value   = d.progress;
            document.getElementById('progressVal').textContent = d.progress;
            document.querySelectorAll('input[name="team"]').forEach(cb => {
                cb.checked = d.team.includes(parseInt(cb.value));
            });
            document.getElementById('modalTitle').textContent = 'تعديل المشروع';
            openModal('modalOverlay', 'modalPanel');
        });
}

/* ── DELETE ── */
let pendingDeleteId = null;
function deleteProject(id, name) {
    closeAllMenus();
    pendingDeleteId = id;
    document.getElementById('delName').textContent = name;
    openModal('deleteOverlay', 'deleteModal');
}

document.getElementById('delConfirm').onclick = function() {
    if (!pendingDeleteId) return;
    fetch(getDeleteUrl(pendingDeleteId), {
        method: 'POST',
        headers: { 'X-CSRFToken': CSRF }
    })
    .then(r => r.json())
    .then(d => {
        if (d.ok) window.location.href = URL_LIST;
    });
};
document.getElementById('delCancel').onclick  = () => closeModal('deleteOverlay','deleteModal');
document.getElementById('deleteOverlay').onclick = () => closeModal('deleteOverlay','deleteModal');

/* ── 3-dot dropdown menu (fixed position to escape stacking context) ── */
function openMenu(btn, id) {
    const menu = document.getElementById('menu-' + id);
    const isOpen = menu.classList.contains('open');
    closeAllMenus();
    if (!isOpen) {
        const rect = btn.getBoundingClientRect();
        menu.style.position = 'fixed';
        menu.style.top  = (rect.bottom + 6) + 'px';
        menu.style.left = rect.left + 'px';
        menu.style.right = 'auto';
        menu.classList.add('open');
        setTimeout(() => document.addEventListener('click', closeAllMenusOnce), 10);
    }
}
function closeAllMenus() {
    document.querySelectorAll('.pdropdown').forEach(m => m.classList.remove('open'));
}
function closeAllMenusOnce() {
    closeAllMenus();
    document.removeEventListener('click', closeAllMenusOnce);
}
document.querySelectorAll('.pdots').forEach(btn => {
    btn.addEventListener('click', e => e.stopPropagation());
});
document.querySelectorAll('.pdropdown').forEach(d => {
    d.addEventListener('click', e => e.stopPropagation());
});

/* ── VIEW TOGGLE ── */
const btnGrid = document.getElementById('btnGrid');
const btnList = document.getElementById('btnList');
const grid    = document.getElementById('projectsGrid');
const table   = document.getElementById('projectsTable');

btnGrid.onclick = () => {
    grid.style.display  = '';
    table.style.display = 'none';
    btnGrid.classList.add('active');
    btnList.classList.remove('active');
    localStorage.setItem('projects_view', 'grid');
};
btnList.onclick = () => {
    grid.style.display  = 'none';
    table.style.display = '';
    btnList.classList.add('active');
    btnGrid.classList.remove('active');
    localStorage.setItem('projects_view', 'list');
};

/* restore saved view */
if (localStorage.getItem('projects_view') === 'list') btnList.click();

/* ── FILTER TABS ── */
document.querySelectorAll('.ftab').forEach(tab => {
    tab.addEventListener('click', function() {
        const status = this.dataset.status;
        const q      = document.getElementById('searchInput').value;
        const params = new URLSearchParams();
        if (status) params.set('status', status);
        if (q)      params.set('q', q);
        window.location.href = URL_LIST + (params.toString() ? '?' + params.toString() : '');
    });
});

/* ── SEARCH ── */
let searchTimer;
document.getElementById('searchInput').addEventListener('input', function() {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
        const params = new URLSearchParams(window.location.search);
        if (this.value) params.set('q', this.value);
        else params.delete('q');
        window.location.href = URL_LIST + (params.toString() ? '?' + params.toString() : '');
    }, 500);
});

/* ── ESC to close ── */
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
        closeModal('modalOverlay', 'modalPanel');
        closeModal('deleteOverlay', 'deleteModal');
        closeClientPicker();
        closeAllMenus();
    }
});

/* ══ CLIENT PICKER ══ */
function openClientPicker() {
    document.getElementById('clientPickerModal').classList.add('active');
    document.getElementById('clientPickerOverlay').classList.add('active');
    document.body.style.overflow = 'hidden';
    setTimeout(() => document.getElementById('cpSearch').focus(), 100);
}
function closeClientPicker() {
    document.getElementById('clientPickerModal').classList.remove('active');
    document.getElementById('clientPickerOverlay').classList.remove('active');
    document.body.style.overflow = '';
}
function selectClient(name) {
    document.getElementById('fClient').value = name;
    const lbl = document.getElementById('clientPickerLabel');
    lbl.textContent = name;
    document.getElementById('clientPickerBtn').classList.add('has-value');
    closeClientPicker();
}
function filterClients(q) {
    const items = document.querySelectorAll('#cpList .cp-item');
    const lower = q.trim().toLowerCase();
    items.forEach(item => {
        item.style.display = item.dataset.name.toLowerCase().includes(lower) ? '' : 'none';
    });
}
