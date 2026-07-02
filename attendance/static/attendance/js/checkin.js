/* ══════════════════════════════
   checkin.js
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

/* ── capture flow ── */
let currentType = null;
let mediaStream = null;
let capturedBlob = null;
let currentLat = null;
let currentLng = null;

const els = {};
function cacheEls() {
    els.overlay   = document.getElementById('captureOverlay');
    els.panel     = document.getElementById('capturePanel');
    els.title     = document.getElementById('captureTitle');
    els.video     = document.getElementById('camVideo');
    els.photo     = document.getElementById('camPhoto');
    els.canvas    = document.getElementById('camCanvas');
    els.btnCapture= document.getElementById('btnCapture');
    els.btnRetake = document.getElementById('btnRetake');
    els.btnSubmit = document.getElementById('btnSubmitRecord');
    els.locStatus = document.getElementById('locationStatus');
    els.camStatus = document.getElementById('cameraStatus');
    els.note      = document.getElementById('captureNote');
    els.todayList = document.getElementById('todayList');
}

function openCapture(type) {
    cacheEls();
    currentType = type;
    els.title.textContent = type === 'IN' ? 'تسجيل حضور' : 'تسجيل انصراف';
    capturedBlob = null;
    currentLat = null;
    currentLng = null;
    els.note.value = '';
    els.btnSubmit.disabled = true;
    els.photo.classList.add('hidden');
    els.video.classList.remove('hidden');
    els.btnRetake.style.display = 'none';
    els.btnCapture.style.display = '';
    els.locStatus.textContent = 'جارٍ تحديد الموقع...';
    els.camStatus.textContent = '';

    els.overlay.classList.add('active');
    els.panel.classList.add('active');

    startCamera();
    startLocation();
}

function closeCapture() {
    stopCamera();
    els.overlay.classList.remove('active');
    els.panel.classList.remove('active');
}

function startCamera() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        els.camStatus.textContent = 'الكاميرا غير مدعومة على هذا الجهاز';
        return;
    }
    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false })
        .then(stream => {
            mediaStream = stream;
            els.video.srcObject = stream;
        })
        .catch(() => {
            els.camStatus.textContent = 'تعذر الوصول إلى الكاميرا، يرجى السماح بالوصول';
        });
}

function stopCamera() {
    if (mediaStream) {
        mediaStream.getTracks().forEach(t => t.stop());
        mediaStream = null;
    }
}

function startLocation() {
    if (!navigator.geolocation) {
        els.locStatus.textContent = 'تحديد الموقع غير مدعوم على هذا الجهاز';
        return;
    }
    navigator.geolocation.getCurrentPosition(
        pos => {
            currentLat = pos.coords.latitude;
            currentLng = pos.coords.longitude;
            els.locStatus.textContent = '✓ تم تحديد الموقع';
        },
        () => {
            els.locStatus.textContent = 'تعذر تحديد الموقع (سيتم الحفظ بدون موقع)';
        },
        { enableHighAccuracy: true, timeout: 10000 }
    );
}

function capturePhoto() {
    if (!mediaStream) return;
    const MAX_WIDTH = 640;
    const vw = els.video.videoWidth || MAX_WIDTH;
    const vh = els.video.videoHeight || MAX_WIDTH;
    const scale = Math.min(1, MAX_WIDTH / vw);
    els.canvas.width = vw * scale;
    els.canvas.height = vh * scale;
    const ctx = els.canvas.getContext('2d');
    ctx.drawImage(els.video, 0, 0, els.canvas.width, els.canvas.height);

    els.canvas.toBlob(blob => {
        capturedBlob = blob;
        els.photo.src = URL.createObjectURL(blob);
        els.photo.classList.remove('hidden');
        els.video.classList.add('hidden');
        els.btnCapture.style.display = 'none';
        els.btnRetake.style.display = '';
        els.btnSubmit.disabled = false;
    }, 'image/jpeg', 0.5);
}

function retakePhoto() {
    capturedBlob = null;
    els.btnSubmit.disabled = true;
    els.photo.classList.add('hidden');
    els.video.classList.remove('hidden');
    els.btnCapture.style.display = '';
    els.btnRetake.style.display = 'none';
}

function submitRecord() {
    if (!capturedBlob || !currentType) return;
    els.btnSubmit.disabled = true;

    const fd = new FormData();
    fd.append('csrfmiddlewaretoken', CSRF);
    fd.append('record_type', currentType);
    fd.append('photo', capturedBlob, 'capture.jpg');
    fd.append('note', els.note.value.trim());
    if (currentLat !== null) fd.append('latitude', currentLat);
    if (currentLng !== null) fd.append('longitude', currentLng);

    fetch(URL_RECORD_CREATE, { method: 'POST', body: fd })
        .then(r => r.json())
        .then(data => {
            if (data.ok) {
                addTodayRow(data);
                closeCapture();
            } else {
                alert(data.error || 'حدث خطأ أثناء الحفظ');
                els.btnSubmit.disabled = false;
            }
        })
        .catch(() => {
            alert('تعذر الاتصال بالخادم');
            els.btnSubmit.disabled = false;
        });
}

function addTodayRow(data) {
    const empty = document.getElementById('todayEmpty');
    if (empty) empty.remove();
    const row = document.createElement('div');
    row.className = 'att-today-row';
    const badgeClass = data.record_type === 'IN' ? 'att-badge-in' : 'att-badge-out';
    const badgeLabel = data.record_type === 'IN' ? 'حضور' : 'انصراف';
    row.innerHTML = `
        <span class="att-badge ${badgeClass}">${badgeLabel}</span>
        <span class="att-today-time">${data.created_at}</span>
        ${data.work_hours ? `<span class="att-today-hours">${data.work_hours} ساعة عمل</span>` : ''}
    `;
    els.todayList.appendChild(row);
}

document.addEventListener('DOMContentLoaded', () => {
    cacheEls();
    const btnIn = document.getElementById('btnOpenIn');
    const btnOut = document.getElementById('btnOpenOut');
    if (btnIn) btnIn.addEventListener('click', () => openCapture('IN'));
    if (btnOut) btnOut.addEventListener('click', () => openCapture('OUT'));
});

document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeCapture();
});
