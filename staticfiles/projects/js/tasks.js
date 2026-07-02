/* ══════════════════════════════
   tasks.js
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
    /* support both old 'true' and new '1' */
    const saved = localStorage.getItem(KEY);
    setExpanded(saved === '1' || saved === 'true');
    btn.addEventListener('click', () => setExpanded(!sidebar.classList.contains('expanded')));
    document.addEventListener('keydown', e => {
        if ((e.key === '[' || e.key === 'b') && !e.target.matches('input, textarea'))
            setExpanded(!sidebar.classList.contains('expanded'));
    });
})();

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

/* ── reset form ── */
function resetForm() {
    document.getElementById('taskForm').reset();
    document.getElementById('editId').value = '';
    document.getElementById('modalTitle').textContent = 'مهمة جديدة';
}

/* ── open add modal ── */
function openAddModal() {
    resetForm();
    openModal('modalOverlay', 'modalPanel');
}
document.getElementById('btnAddTask').onclick = openAddModal;
document.getElementById('modalClose').onclick  = () => closeModal('modalOverlay', 'modalPanel');
document.getElementById('modalCancel').onclick = () => closeModal('modalOverlay', 'modalPanel');
document.getElementById('modalOverlay').onclick = () => closeModal('modalOverlay', 'modalPanel');

/* ── SUBMIT ── */
document.getElementById('taskForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const id  = document.getElementById('editId').value;
    const url = id ? getEditUrl(id) : URL_CREATE;
    const fd  = new FormData(this);
    fetch(url, { method: 'POST', body: fd })
        .then(r => r.json())
        .then(d => { if (d.ok) window.location.href = URL_LIST; });
});

/* ── EDIT ── */
function editTask(id) {
    fetch(getDetailUrl(id))
        .then(r => r.json())
        .then(d => {
            document.getElementById('editId').value    = d.id;
            document.getElementById('fTitle').value    = d.title;
            document.getElementById('fProject').value  = d.project;
            document.getElementById('fStatus').value   = d.status;
            document.getElementById('fPriority').value = d.priority;
            document.getElementById('fAssigned').value = d.assigned_to;
            document.getElementById('fDue').value          = d.due_date;
            document.getElementById('fTimeHour').value     = d.due_time_hour || '';
            document.getElementById('fTimeMin').value      = d.due_time_min  || '';
            document.getElementById('fTimeAmpm').value     = d.due_time_ampm || 'AM';
            document.getElementById('fDesc').value         = d.description;
            document.getElementById('modalTitle').textContent = 'تعديل المهمة';
            openModal('modalOverlay', 'modalPanel');
        });
}

/* ── TOGGLE STATUS (quick check) ── */
function toggleStatus(id, currentStatus) {
    const next = currentStatus === 'done' ? 'todo' : 'done';
    const fd = new FormData();
    fd.append('csrfmiddlewaretoken', CSRF);
    fd.append('status', next);
    fetch(getDetailUrl(id))
        .then(r => r.json())
        .then(d => {
            const editFd = new FormData();
            editFd.append('csrfmiddlewaretoken', CSRF);
            editFd.append('title',       d.title);
            editFd.append('project',     d.project);
            editFd.append('status',      next);
            editFd.append('priority',    d.priority);
            editFd.append('assigned_to', d.assigned_to);
            editFd.append('due_date',    d.due_date);
            editFd.append('description', d.description);
            return fetch(getEditUrl(id), { method: 'POST', body: editFd });
        })
        .then(r => r.json())
        .then(d => { if (d.ok) window.location.reload(); });
}

/* ── DELETE ── */
let pendingId = null;
function deleteTask(id, name) {
    pendingId = id;
    document.getElementById('delName').textContent = name;
    openModal('deleteOverlay', 'deleteModal');
}
document.getElementById('delConfirm').onclick = function() {
    if (!pendingId) return;
    const fd = new FormData();
    fd.append('csrfmiddlewaretoken', CSRF);
    fetch(getDeleteUrl(pendingId), { method: 'POST', body: fd })
        .then(r => r.json())
        .then(d => { if (d.ok) window.location.href = URL_LIST; });
};
document.getElementById('delCancel').onclick   = () => closeModal('deleteOverlay', 'deleteModal');
document.getElementById('deleteOverlay').onclick = () => closeModal('deleteOverlay', 'deleteModal');

/* ── FILTERS ── */
function applyFilters() {
    const params   = new URLSearchParams();
    const status   = document.querySelector('.ftab.active')?.dataset.status || '';
    const priority = document.getElementById('filterPriority').value;
    const project  = document.getElementById('filterProject').value;
    const assignee = document.getElementById('filterAssignee').value;
    const q        = document.getElementById('searchInput').value;
    if (status)   params.set('status',   status);
    if (priority) params.set('priority', priority);
    if (project)  params.set('project',  project);
    if (assignee) params.set('assignee', assignee);
    if (q)        params.set('q',        q);
    window.location.href = URL_LIST + (params.toString() ? '?' + params.toString() : '');
}
document.querySelectorAll('.ftab').forEach(tab => {
    tab.addEventListener('click', function() {
        document.querySelectorAll('.ftab').forEach(t => t.classList.remove('active'));
        this.classList.add('active');
        applyFilters();
    });
});
let searchTimer;
document.getElementById('searchInput').addEventListener('input', function() {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(applyFilters, 500);
});

/* ── ESC ── */
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
        closeModal('modalOverlay', 'modalPanel');
        closeModal('deleteOverlay', 'deleteModal');
    }
});
