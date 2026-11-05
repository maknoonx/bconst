// Preloader — يختفي بعد تحميل الصفحة ثم يُزال من الـ DOM
(function () {
    var done = false;
    function hide() {
        if (done) return;
        done = true;
        var preloader = document.getElementById('preloader');
        if (!preloader) return;
        preloader.classList.add('fade-out');
        setTimeout(function () { preloader.remove(); }, 600);
    }
    window.addEventListener('load', function () { setTimeout(hide, 300); });
    // احتياط: أقصى مدة 2.5 ثانية حتى لو لم يكتمل التحميل
    setTimeout(hide, 2500);
})();
