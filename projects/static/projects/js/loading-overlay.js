/* ══════════════════════════════
   loading-overlay.js
   Global blur overlay shown during any fetch() call, form submit,
   or link navigation across the internal dashboard.
══════════════════════════════ */

(function () {
    if (document.getElementById('globalLoadingOverlay')) return;

    document.body.insertAdjacentHTML('beforeend',
        '<div id="globalLoadingOverlay"><div class="gl-spinner"></div></div>'
    );

    const overlay = document.getElementById('globalLoadingOverlay');
    let pendingCount = 0;
    let showTimer = null;
    let safetyTimer = null;

    function show() {
        pendingCount++;
        if (showTimer || overlay.classList.contains('active')) return;
        showTimer = setTimeout(() => {
            overlay.classList.add('active');
            showTimer = null;
        }, 150);
        clearTimeout(safetyTimer);
        safetyTimer = setTimeout(hideAll, 15000);
    }

    function hide() {
        pendingCount = Math.max(0, pendingCount - 1);
        if (pendingCount === 0) hideAll();
    }

    function hideAll() {
        pendingCount = 0;
        clearTimeout(showTimer);
        clearTimeout(safetyTimer);
        showTimer = null;
        overlay.classList.remove('active');
    }

    /* ── wrap fetch: covers every AJAX call in every app's JS automatically ── */
    const nativeFetch = window.fetch;
    window.fetch = function (...args) {
        show();
        return nativeFetch.apply(this, args)
            .then(res => { hide(); return res; })
            .catch(err => { hide(); throw err; });
    };

    /* ── real link navigation (sidebar, pagination, etc.) ── */
    document.addEventListener('click', function (e) {
        const link = e.target.closest('a[href]');
        if (!link) return;
        const href = link.getAttribute('href');
        if (!href || href.startsWith('#') || href.startsWith('javascript:')) return;
        if (link.target === '_blank' || e.metaKey || e.ctrlKey || e.shiftKey) return;
        show();
    }, true);

    /* ── plain <form> POST/GET submissions (non-AJAX) ── */
    document.addEventListener('submit', function () {
        show();
    }, true);

    /* clear the overlay if the user actually leaves the page (real navigation) */
    window.addEventListener('pageshow', hideAll);
})();
