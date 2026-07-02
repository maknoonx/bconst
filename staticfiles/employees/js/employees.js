/* ══════════════════════════════
   employees.js
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
document.querySelectorAll('.emp-tab').forEach(tab => {
    tab.addEventListener('click', function() {
        document.querySelectorAll('.emp-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.emp-section').forEach(s => s.classList.remove('active'));
        this.classList.add('active');
        document.getElementById('tab-' + this.dataset.tab).classList.add('active');

        // show/hide header add button based on active tab
        const btn = document.getElementById('btnAddEmployee');
        if (btn) btn.style.display = this.dataset.tab === 'employees' ? '' : 'none';
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

function closeEmpModal()      { closeModal('empOverlay', 'empPanel'); }
function closeUserModal()     { closeModal('userOverlay', 'userPanel'); }
function closeEditUserModal() { closeModal('editUserOverlay', 'editUserPanel'); }
function closeGroupModal()    { closeModal('groupOverlay', 'groupPanel'); }
function closeDelModal()      { closeModal('delOverlay', 'delModal'); }

/* ── employee filter ── */
function applyEmpFilters() {
    const q      = document.getElementById('empSearch').value;
    const status = document.getElementById('empStatusFilter').value;
    const params = new URLSearchParams();
    if (q)      params.set('q', q);
    if (status) params.set('status', status);
    window.location.href = URL_EMP_LIST + (params.toString() ? '?' + params.toString() : '');
}

let empSearchTimer;
document.getElementById('empSearch').addEventListener('input', function() {
    clearTimeout(empSearchTimer);
    empSearchTimer = setTimeout(applyEmpFilters, 500);
});

/* ── Add Employee ── */
function openAddEmployee() {
    document.getElementById('empForm').reset();
    document.getElementById('editEmpId').value = '';
    document.getElementById('empModalTitle').textContent = 'موظف جديد';
    openModal('empOverlay', 'empPanel');
}

function editEmployee(id) {
    fetch(getEmpDetailUrl(id))
        .then(r => r.json())
        .then(d => {
            document.getElementById('editEmpId').value     = d.id;
            document.getElementById('fFirstName').value    = d.first_name;
            document.getElementById('fLastName').value     = d.last_name;
            document.getElementById('fJobTitle').value     = d.job_title;
            document.getElementById('fNationality').value  = d.nationality;
            document.getElementById('fGender').value       = d.gender;
            document.getElementById('fIdType').value       = d.id_type;
            document.getElementById('fIdNumber').value     = d.id_number;
            document.getElementById('fDob').value          = d.date_of_birth;
            document.getElementById('fEmpDate').value      = d.employment_date;
            document.getElementById('fPhone').value        = d.phone_number;
            document.getElementById('fEmail').value        = d.email;
            document.getElementById('fAddress').value      = d.address;
            document.getElementById('fStatus').value       = d.status;
            document.getElementById('empModalTitle').textContent = 'تعديل بيانات الموظف';
            openModal('empOverlay', 'empPanel');
        });
}

function submitEmployee() {
    const id  = document.getElementById('editEmpId').value;
    const url = id ? getEmpEditUrl(id) : URL_EMP_CREATE;
    const fd  = new FormData(document.getElementById('empForm'));
    fetch(url, { method: 'POST', body: fd })
        .then(r => r.json())
        .then(d => { if (d.ok) window.location.reload(); else alert(d.error || 'حدث خطأ'); });
}

/* ── Add User Account ── */
function openAddUser(empId, empName, empEmail) {
    document.getElementById('userForm').reset();
    document.getElementById('uEmpId').value   = empId;
    document.getElementById('uUserId').value  = '';
    document.getElementById('uEmail').value   = empEmail || '';
    document.getElementById('userModalTitle').textContent = 'إضافة حساب لـ ' + empName;
    document.querySelectorAll('.uGroupCheck').forEach(c => c.checked = false);
    openModal('userOverlay', 'userPanel');
}

function submitUser() {
    const fd = new FormData();
    fd.append('csrfmiddlewaretoken', CSRF);
    fd.append('employee_id', document.getElementById('uEmpId').value);
    fd.append('username',    document.getElementById('uUsername').value);
    fd.append('email',       document.getElementById('uEmail').value);
    fd.append('is_staff',    document.getElementById('uIsStaff').checked ? '1' : '0');
    document.querySelectorAll('.uGroupCheck:checked').forEach(c => fd.append('groups', c.value));

    fetch(URL_USER_CREATE, { method: 'POST', body: fd })
        .then(r => r.json())
        .then(d => {
            if (d.ok) {
                closeUserModal();
                alert('تم إنشاء الحساب بنجاح. سيُرسَل بريد إلكتروني لإعداد كلمة المرور.');
                window.location.reload();
            } else {
                alert(d.error || 'حدث خطأ');
            }
        });
}

/* ── Edit User ── */
function editUser(id, isActive, isStaff, groupIds) {
    document.getElementById('euId').value        = id;
    document.getElementById('euIsActive').checked = isActive;
    document.getElementById('euIsStaff').checked  = isStaff;
    document.querySelectorAll('.euGroupCheck').forEach(c => {
        c.checked = groupIds.includes(parseInt(c.value));
    });
    openModal('editUserOverlay', 'editUserPanel');
}

function submitEditUser() {
    const id = document.getElementById('euId').value;
    const fd = new FormData();
    fd.append('csrfmiddlewaretoken', CSRF);
    fd.append('is_active', document.getElementById('euIsActive').checked ? '1' : '0');
    fd.append('is_staff',  document.getElementById('euIsStaff').checked  ? '1' : '0');
    document.querySelectorAll('.euGroupCheck:checked').forEach(c => fd.append('groups', c.value));
    fetch(getUserEditUrl(id), { method: 'POST', body: fd })
        .then(r => r.json())
        .then(d => { if (d.ok) window.location.reload(); });
}

/* ── Resend email ── */
function resendEmail(id) {
    const fd = new FormData();
    fd.append('csrfmiddlewaretoken', CSRF);
    fetch(getUserResendUrl(id), { method: 'POST', body: fd })
        .then(r => r.json())
        .then(d => { alert(d.ok ? 'تم إرسال البريد الإلكتروني بنجاح' : (d.error || 'حدث خطأ')); });
}

/* ── Toggle employee status ── */
function toggleEmpStatus(id, currentStatus) {
    const fd = new FormData();
    fd.append('csrfmiddlewaretoken', CSRF);
    fetch(getEmpToggleUrl(id), { method: 'POST', body: fd })
        .then(r => r.json())
        .then(d => { if (d.ok) window.location.reload(); });
}

/* ── Delete ── */
let pendingDelete = null;
function deleteEmployee(id, name) {
    pendingDelete = { url: getEmpDeleteUrl(id) };
    document.getElementById('delName').textContent = name;
    openModal('delOverlay', 'delModal');
}
function deleteUser(id, name) {
    pendingDelete = { url: getUserDeleteUrl(id) };
    document.getElementById('delName').textContent = name;
    openModal('delOverlay', 'delModal');
}
function deleteGroup(id, name) {
    pendingDelete = { url: getGrpDeleteUrl(id) };
    document.getElementById('delName').textContent = name;
    openModal('delOverlay', 'delModal');
}
document.getElementById('delConfirmBtn').onclick = function() {
    if (!pendingDelete) return;
    const fd = new FormData();
    fd.append('csrfmiddlewaretoken', CSRF);
    fetch(pendingDelete.url, { method: 'POST', body: fd })
        .then(r => r.json())
        .then(d => { if (d.ok) window.location.reload(); });
};

/* ── Groups ── */
function openAddGroup() {
    document.getElementById('groupForm').reset();
    document.getElementById('editGroupId').value = '';
    document.getElementById('groupModalTitle').textContent = 'مجموعة جديدة';
    document.querySelectorAll('.permCheck').forEach(c => c.checked = false);
    openModal('groupOverlay', 'groupPanel');
}

function editGroup(id, name) {
    fetch(getGrpDetailUrl(id))
        .then(r => r.json())
        .then(d => {
            document.getElementById('editGroupId').value = d.id;
            document.getElementById('gName').value       = d.name;
            document.querySelectorAll('.permCheck').forEach(c => {
                c.checked = d.permissions.includes(parseInt(c.value));
            });
            document.getElementById('groupModalTitle').textContent = 'تعديل المجموعة';
            openModal('groupOverlay', 'groupPanel');
        });
}

function submitGroup() {
    const id  = document.getElementById('editGroupId').value;
    const url = id ? getGrpEditUrl(id) : URL_GRP_CREATE;
    const fd  = new FormData();
    fd.append('csrfmiddlewaretoken', CSRF);
    fd.append('name', document.getElementById('gName').value);
    document.querySelectorAll('.permCheck:checked').forEach(c => fd.append('permissions', c.value));
    fetch(url, { method: 'POST', body: fd })
        .then(r => r.json())
        .then(d => { if (d.ok) window.location.reload(); else alert(d.error || 'حدث خطأ'); });
}

/* ── Permission search ── */
document.getElementById('permSearch').addEventListener('input', function() {
    const q = this.value.toLowerCase();
    document.querySelectorAll('#permGrid .perm-item').forEach(item => {
        item.style.display = item.textContent.toLowerCase().includes(q) ? '' : 'none';
    });
});

/* ── ESC ── */
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
        closeEmpModal(); closeUserModal(); closeEditUserModal();
        closeGroupModal(); closeDelModal();
    }
});
