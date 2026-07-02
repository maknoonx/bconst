/* invoices.js */
'use strict';

/* ── sidebar toggle ── */
(function(){
    var sb  = document.getElementById('sidebar');
    var btn = document.getElementById('sidebarToggle');
    if(!sb || !btn) return;
    function setExpanded(e){
        sb.classList.toggle('expanded', e);
        document.body.classList.toggle('sidebar-open', e);
        localStorage.setItem('sidebar_expanded', e ? '1' : '0');
    }
    setExpanded(localStorage.getItem('sidebar_expanded') === '1');
    btn.addEventListener('click', function(){ setExpanded(!sb.classList.contains('expanded')); });
    document.addEventListener('keydown', function(e){
        if((e.key === '[' || e.key === 'b') && !e.target.matches('input,textarea')){
            setExpanded(!sb.classList.contains('expanded'));
        }
    });
})();

/* ── CSRF helper ── */
function getCsrf(){
    var el = document.querySelector('[name=csrfmiddlewaretoken]');
    if(el) return el.value;
    // fallback: read from cookie
    var m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? m[1] : (window.CSRF || '');
}

function post(url, data){
    return fetch(url, {
        method: 'POST',
        headers: {'Content-Type':'application/json','X-CSRFToken': getCsrf()},
        body: JSON.stringify(data)
    }).then(function(r){ return r.json(); });
}

function showErr(msg){ alert('خطأ: ' + msg); }
