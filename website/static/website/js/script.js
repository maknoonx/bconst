/* ====================================================
   شركة باء البناء للمقاولات — script.js
   ==================================================== */

(function () {
    'use strict';

    /* ------------------------------------------------
       القائمة للجوال
       ------------------------------------------------ */
    var toggle   = document.getElementById('menuToggle');
    var navMenu  = document.getElementById('navMenu');
    var overlay  = document.getElementById('navOverlay');

    function openMenu() {
        navMenu.classList.add('open');
        toggle.classList.add('active');
        overlay.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    function closeMenu() {
        navMenu.classList.remove('open');
        toggle.classList.remove('active');
        overlay.classList.remove('show');
        document.body.style.overflow = '';
    }

    if (toggle) {
        toggle.addEventListener('click', function () {
            navMenu.classList.contains('open') ? closeMenu() : openMenu();
        });
    }

    if (overlay) {
        overlay.addEventListener('click', closeMenu);
    }

    /* إغلاق عند الضغط على رابط */
    if (navMenu) {
        navMenu.querySelectorAll('.nav-link').forEach(function (link) {
            link.addEventListener('click', closeMenu);
        });
    }

    /* ------------------------------------------------
       تأثير الشريط عند التمرير
       ------------------------------------------------ */
    window.addEventListener('scroll', function () {
        var header = document.querySelector('.header-inner');
        if (!header) return;
        if (window.scrollY > 60) {
            header.style.background = 'rgba(26,24,18,.96)';
            header.style.boxShadow  = '0 8px 40px rgba(0,0,0,.35)';
        } else {
            header.style.background = 'rgba(26,24,18,.88)';
            header.style.boxShadow  = 'none';
        }
    }, { passive: true });

    /* ------------------------------------------------
       ظهور محتوى الهيرو بعد تحميل الصفحة
       ------------------------------------------------ */
    document.addEventListener('DOMContentLoaded', function () {
        setTimeout(function () {
            var content = document.getElementById('heroContent');
            if (content) {
                content.style.opacity    = '1';
                content.style.transform  = 'translateY(0)';
            }
        }, 400);
    });

    /* ------------------------------------------------
       التمرير السلس للروابط الداخلية
       ------------------------------------------------ */
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (e) {
            var href = this.getAttribute('href');
            if (href === '#' || href === '') return;
            var target = document.querySelector(href);
            if (!target) return;
            e.preventDefault();
            var offset = 90;
            var top = target.getBoundingClientRect().top + window.pageYOffset - offset;
            window.scrollTo({ top: top, behavior: 'smooth' });
        });
    });

    /* ------------------------------------------------
       ظهور العناصر عند الظهور في الشاشة
       ------------------------------------------------ */
    if ('IntersectionObserver' in window) {
        var ioOptions = { threshold: 0.12, rootMargin: '0px 0px -60px 0px' };
        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.style.opacity   = '1';
                    entry.target.style.transform = 'translateY(0)';
                    io.unobserve(entry.target);
                }
            });
        }, ioOptions);

        document.addEventListener('DOMContentLoaded', function () {
            var els = document.querySelectorAll(
                '.about-card, .feature-row, .partner-item, .section-header'
            );
            els.forEach(function (el) {
                el.style.opacity   = '0';
                el.style.transform = 'translateY(24px)';
                el.style.transition = 'opacity .6s ease, transform .6s ease';
                io.observe(el);
            });
        });
    }

    /* ------------------------------------------------
       النشرة البريدية
       ------------------------------------------------ */
    var newsletterForms = document.querySelectorAll('.newsletter-form');
    newsletterForms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            var input = this.querySelector('input[type="email"]');
            if (input && input.value) {
                alert('شكراً للاشتراك في نشرتنا الإخبارية!');
                input.value = '';
            }
        });
    });

})();
