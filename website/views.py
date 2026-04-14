from django.shortcuts import render
from django.urls import reverse
from .translations import CONTENT


def _build_ctx(lang, page):
    """إنشاء سياق كامل للصفحة بناءً على اللغة والصفحة الحالية."""
    ctx = CONTENT[lang].copy()

    # عنوان الصفحة
    ctx['page_title']  = ctx[f'page_title_{page}']
    ctx['active_page'] = page

    # روابط بنفس اللغة الحالية
    ctx['url_home']        = reverse('home'        if lang == 'ar' else 'home_en')
    ctx['url_studio']      = reverse('studio'      if lang == 'ar' else 'studio_en')
    ctx['url_coming_soon'] = reverse('coming_soon' if lang == 'ar' else 'coming_soon_en')

    # رابط التبديل للغة الأخرى (نفس الصفحة)
    switch_map = {
        'home':        'home_en'        if lang == 'ar' else 'home',
        'studio':      'studio_en'      if lang == 'ar' else 'studio',
        'coming_soon': 'coming_soon_en' if lang == 'ar' else 'coming_soon',
    }
    ctx['url_lang_switch'] = reverse(switch_map[page])

    return ctx


def home(request, lang='ar'):
    return render(request, 'website/home.html', _build_ctx(lang, 'home'))


def studio(request, lang='ar'):
    return render(request, 'website/studio.html', _build_ctx(lang, 'studio'))


def coming_soon(request, lang='ar'):
    return render(request, 'website/coming-soon.html', _build_ctx(lang, 'coming_soon'))
