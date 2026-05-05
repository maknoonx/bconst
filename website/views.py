from django.shortcuts import render, Http404
from django.urls import reverse
from .translations import CONTENT

SITE_BASE = 'https://www.bconstructions.org'

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

    # SEO: canonical and hreflang URLs
    ar_route_map = {'home': 'home', 'studio': 'studio', 'contact': 'contact',
                    'privacy': 'privacy', 'terms': 'terms', 'services': 'services',
                    'coming_soon': 'coming_soon'}
    en_route_map = {'home': 'home_en', 'studio': 'studio_en', 'contact': 'contact_en',
                    'privacy': 'privacy_en', 'terms': 'terms_en', 'services': 'services_en',
                    'coming_soon': 'coming_soon_en'}

    if page == 'services' and slug:
        ar_url = SITE_BASE + reverse('service_detail', kwargs={'slug': slug})
        en_url = SITE_BASE + reverse('service_detail_en', kwargs={'slug': slug})
    elif page in ar_route_map:
        ar_url = SITE_BASE + reverse(ar_route_map[page])
        en_url = SITE_BASE + reverse(en_route_map[page])
    else:
        ar_url = SITE_BASE + '/'
        en_url = SITE_BASE + '/en/'

    ctx['canonical_url'] = ar_url if lang == 'ar' else en_url
    ctx['hreflang_ar_url'] = ar_url
    ctx['hreflang_en_url'] = en_url

    # SEO: meta tags from translations (with fallbacks)
    seo_page = 'services' if (page == 'services') else page
    ctx['page_title']       = ctx.get(f'seo_title_{seo_page}', ctx.get(f'page_title_{seo_page}', ctx.get('company_name', '')))
    ctx['meta_description'] = ctx.get(f'meta_description_{seo_page}', '')
    ctx['meta_keywords']    = ctx.get(f'meta_keywords_{seo_page}', '')
    ctx['og_title']         = ctx.get(f'og_title_{seo_page}', ctx['page_title'])
    ctx['og_description']   = ctx['meta_description']
    ctx['og_image_url']     = f"{SITE_BASE}/static/website/img/og-{seo_page}-{lang}.jpg"
    ctx['meta_robots']      = 'index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1'
    ctx['site_base_url']    = SITE_BASE

    return ctx


def home(request, lang='ar'):
    return render(request, 'website/home.html', _build_ctx(lang, 'home'))


def studio(request, lang='ar'):
    return render(request, 'website/studio.html', _build_ctx(lang, 'studio'))


def coming_soon(request, lang='ar'):
    ctx = _build_ctx(lang, 'coming_soon')
    ctx['meta_robots'] = 'noindex,follow'
    return render(request, 'website/coming-soon.html', ctx)


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

    # In service_detail view, after setting page_title:
    ctx['meta_description'] = ctx.get(f'svc_{key}_desc', '')[:200]  # use service desc as meta
    ctx['og_title'] = ctx['service_title']
    ctx['og_description'] = ctx['meta_description']
    ctx['og_image_url'] = f"{SITE_BASE}/static/website/img/og-services-{lang}.jpg"

    return render(request, 'website/service-detail.html', ctx)
