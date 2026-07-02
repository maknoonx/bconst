/* ── Sidebar toggle ── */
(function () {
    const sidebar = document.getElementById('sidebar');
    const btn     = document.getElementById('sidebarToggle');
    const STORAGE_KEY = 'sidebar_expanded';

    function setExpanded(expanded) {
        sidebar.classList.toggle('expanded', expanded);
        document.body.classList.toggle('sidebar-open', expanded);
        localStorage.setItem(STORAGE_KEY, expanded ? '1' : '0');
    }

    // restore saved state
    setExpanded(localStorage.getItem(STORAGE_KEY) === '1');

    btn.addEventListener('click', () => {
        setExpanded(!sidebar.classList.contains('expanded'));
    });

    // keyboard shortcut: [ (bracket) to toggle
    document.addEventListener('keydown', e => {
        if ((e.key === '[' || e.key === 'b') && !e.target.matches('input, textarea')) {
            setExpanded(!sidebar.classList.contains('expanded'));
        }
    });
})();

/* Calendar generator */
(function () {
    if (!document.getElementById('calMonth')) return;  // only on dashboard page

    const months = ['يناير','فبراير','مارس','أبريل','مايو','يونيو',
                    'يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر'];

    const now   = new Date();
    const year  = now.getFullYear();
    const month = now.getMonth();
    const today = now.getDate();

    document.getElementById('calMonth').textContent = months[month] + ' ' + year;

    const firstDay = new Date(year, month, 1).getDay(); // 0=Sun
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    // sample event days
    const events = [5, 12, 18, 24, today + 3].filter(d => d > 0 && d <= daysInMonth);

    const container = document.getElementById('calDays');
    // pad start (Sun=0)
    for (let i = 0; i < firstDay; i++) {
        const blank = document.createElement('div');
        blank.className = 'cal-day other';
        container.appendChild(blank);
    }

    for (let d = 1; d <= daysInMonth; d++) {
        const el = document.createElement('div');
        el.textContent = d;
        let cls = 'cal-day';
        if (d === today) cls += ' today';
        else if (events.includes(d)) cls += ' event';
        el.className = cls;
        container.appendChild(el);
    }
})();
