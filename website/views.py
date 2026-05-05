from django.shortcuts import render, Http404
from django.urls import reverse
from .translations import CONTENT

# Slug → service_key mapping
SLUG_TO_KEY = {
    'architectural-design': 'architectural_design',
    'construction':         'construction',
    'real-estate':          'real_estate',
    'renovation':           'renovation',
    'consultancy':          'consultancy',
}

# All services in display order (slug, icon-class)
SERVICES_LIST = [
    ('architectural-design', 'svc_architectural_design'),
    ('construction',         'svc_construction'),
    ('real-estate',          'svc_real_estate'),
    ('renovation',           'svc_renovation'),
    ('consultancy',          'svc_consultancy'),
]


def _build_ctx(lang, page, slug=None):
    """إنشاء سياق كامل للصفحة بناءً على اللغة والصفحة الحالية."""
    ctx = CONTENT[lang].copy()

    # عنوان الصفحة
    ctx['page_title']  = ctx[f'page_title_{page}']
    ctx['active_page'] = page

    # روابط بنفس اللغة الحالية
    ctx['url_home']        = reverse('home'        if lang == 'ar' else 'home_en')
    ctx['url_studio']      = reverse('studio'      if lang == 'ar' else 'studio_en')
    ctx['url_coming_soon'] = reverse('coming_soon' if lang == 'ar' else 'coming_soon_en')
    ctx['url_contact']     = reverse('contact'     if lang == 'ar' else 'contact_en')
    ctx['url_privacy']     = reverse('privacy'     if lang == 'ar' else 'privacy_en')
    ctx['url_terms']       = reverse('terms'       if lang == 'ar' else 'terms_en')
    ctx['url_services']    = reverse('services'    if lang == 'ar' else 'services_en')

    # رابط التبديل للغة الأخرى (نفس الصفحة)
    switch_map = {
        'home':        'home_en'        if lang == 'ar' else 'home',
        'studio':      'studio_en'      if lang == 'ar' else 'studio',
        'coming_soon': 'coming_soon_en' if lang == 'ar' else 'coming_soon',
        'contact':     'contact_en'     if lang == 'ar' else 'contact',
        'privacy':     'privacy_en'     if lang == 'ar' else 'privacy',
        'terms':       'terms_en'       if lang == 'ar' else 'terms',
        'services':    'services_en'    if lang == 'ar' else 'services',
    }

    if page == 'services' and slug:
        # service detail — switch to same slug in other language
        other_name = 'service_detail_en' if lang == 'ar' else 'service_detail'
        ctx['url_lang_switch'] = reverse(other_name, kwargs={'slug': slug})
    elif page in switch_map:
        ctx['url_lang_switch'] = reverse(switch_map[page])
    else:
        ctx['url_lang_switch'] = reverse('home_en' if lang == 'ar' else 'home')

    return ctx


def home(request, lang='ar'):
    return render(request, 'website/home.html', _build_ctx(lang, 'home'))


def studio(request, lang='ar'):
    return render(request, 'website/studio.html', _build_ctx(lang, 'studio'))


def coming_soon(request, lang='ar'):
    return render(request, 'website/coming-soon.html', _build_ctx(lang, 'coming_soon'))


def contact(request, lang='ar'):
    return render(request, 'website/contact.html', _build_ctx(lang, 'contact'))


def privacy(request, lang='ar'):
    return render(request, 'website/privacy.html', _build_ctx(lang, 'privacy'))


def terms(request, lang='ar'):
    return render(request, 'website/terms.html', _build_ctx(lang, 'terms'))


def services_list(request, lang='ar'):
    ctx = _build_ctx(lang, 'services')
    # Build list of service cards for template
    services = []
    for slug, key in SERVICES_LIST:
        services.append({
            'slug':  slug,
            'title': ctx[f'{key}_title'],
            'desc':  ctx[f'{key}_desc'],
            'url':   reverse(
                'service_detail' if lang == 'ar' else 'service_detail_en',
                kwargs={'slug': slug}
            ),
        })
    ctx['services'] = services
    return render(request, 'website/services.html', ctx)


def service_detail(request, slug, lang='ar'):
    key = SLUG_TO_KEY.get(slug)
    if not key:
        raise Http404

    ctx = _build_ctx(lang, 'services', slug=slug)

    full_key = f'svc_{key}'
    ctx['service_title'] = ctx[f'{full_key}_title']
    ctx['service_desc']  = ctx[f'{full_key}_desc']
    ctx['service_sub']   = ctx[f'{full_key}_sub']
    ctx['service_slug']  = slug
    ctx['page_title']    = ctx['service_title'] + ' — ' + ctx['company_name']

    return render(request, 'website/service-detail.html', ctx)
