import datetime

from django.shortcuts import render, redirect, Http404
from django.http import HttpResponse
from django.urls import reverse
from .translations import CONTENT

SITE_BASE = 'https://www.bconstructions.org'

# أقسام موقوفة مؤقتاً — اجعلها True لإعادة إظهارها
SHOW_STUDIO   = False   # استديو أعمالنا
SHOW_PARTNERS = False   # شركاؤنا

# موقع الشركة على خرائط قوقل
COMPANY_MAP_URL = 'https://maps.app.goo.gl/dXnXGsnpTLKDdLrZ6'

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
    ('real-estate',          'svc_real_estate'),
    ('architectural-design', 'svc_architectural_design'),
    ('construction',         'svc_construction'),
    ('renovation',           'svc_renovation'),
    ('consultancy',          'svc_consultancy'),
]


def _build_ctx(lang, page, slug=None):
    """إنشاء سياق كامل للصفحة بناءً على اللغة والصفحة الحالية."""
    ctx = CONTENT[lang].copy()

    # عنوان الصفحة
    ctx['page_title']  = ctx.get(f'page_title_{page}', ctx.get('company_name', ''))
    ctx['active_page'] = page
    ctx['show_studio']   = SHOW_STUDIO
    ctx['show_partners'] = SHOW_PARTNERS
    ctx['map_url_company'] = COMPANY_MAP_URL
    ctx['copyright'] = ctx['copyright'].replace('{year}', str(datetime.date.today().year))

    # روابط بنفس اللغة الحالية
    ctx['url_home']        = reverse('home'        if lang == 'ar' else 'home_en')
    ctx['url_studio']      = reverse('studio'      if lang == 'ar' else 'studio_en')
    ctx['url_coming_soon'] = reverse('coming_soon' if lang == 'ar' else 'coming_soon_en')
    ctx['url_contact']     = reverse('contact'     if lang == 'ar' else 'contact_en')
    ctx['url_privacy']     = reverse('privacy'     if lang == 'ar' else 'privacy_en')
    ctx['url_terms']       = reverse('terms'       if lang == 'ar' else 'terms_en')
    ctx['url_services']    = reverse('services'    if lang == 'ar' else 'services_en')
    ctx['url_projects']    = reverse('projects'    if lang == 'ar' else 'projects_en')
    ctx['url_project_khuzami'] = reverse('project_khuzami' if lang == 'ar' else 'project_khuzami_en')

    # رابط التبديل للغة الأخرى (نفس الصفحة)
    switch_map = {
        'home':        'home_en'        if lang == 'ar' else 'home',
        'studio':      'studio_en'      if lang == 'ar' else 'studio',
        'coming_soon': 'coming_soon_en' if lang == 'ar' else 'coming_soon',
        'contact':     'contact_en'     if lang == 'ar' else 'contact',
        'privacy':     'privacy_en'     if lang == 'ar' else 'privacy',
        'terms':       'terms_en'       if lang == 'ar' else 'terms',
        'services':    'services_en'    if lang == 'ar' else 'services',
        'projects':    'projects_en'    if lang == 'ar' else 'projects',
        'project_khuzami': 'project_khuzami_en' if lang == 'ar' else 'project_khuzami',
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
                    'projects': 'projects', 'project_khuzami': 'project_khuzami',
                    'coming_soon': 'coming_soon'}
    en_route_map = {'home': 'home_en', 'studio': 'studio_en', 'contact': 'contact_en',
                    'privacy': 'privacy_en', 'terms': 'terms_en', 'services': 'services_en',
                    'projects': 'projects_en', 'project_khuzami': 'project_khuzami_en',
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
    if not SHOW_STUDIO:
        return redirect('coming_soon' if lang == 'ar' else 'coming_soon_en')
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


# ==========================================================
#   المشاريع  —  Projects
# ==========================================================

# رابط الموقع على خرائط جوجل — استبدله بالرابط الدقيق للمشروع
KHUZAMI_MAP_URL = 'https://www.google.com/maps/search/?api=1&query=%D8%AD%D9%8A%20%D8%A7%D9%84%D8%AE%D8%B2%D8%A7%D9%85%D9%89%D8%8C%20%D8%A7%D9%84%D9%85%D8%AF%D9%8A%D9%86%D8%A9%20%D8%A7%D9%84%D9%85%D9%86%D9%88%D8%B1%D8%A9'

# بيانات مشروع أدوار الخزامى (عربي / إنجليزي)
KHUZAMI = {
    'ar': {
        'name': 'أدوار الخزامى',
        'name_latin': 'ADWAR AL KHUZAMI',
        'city': 'المدينة المنورة',
        'location': 'المدينة المنورة — حي الخزامى',
        'status': 'متاح الآن',
        'hero_kicker': 'مشروع سكني · المدينة المنورة',
        'hero_tagline_1': 'أربعة منازل خاصة.',
        'hero_tagline_2': 'عنوان واحد.',
        'hero_desc': 'عمارة سكنية راقية في حي الخزامى بالمدينة المنورة — شقة كاملة تشغل الدور بأكمله، لكلٍّ منها حديقتها أو شرفاتها أو سطحها الخاص.',
        'hero_meta': '٤ أدوار · ٤ منازل · ١٩٢–١٩٨ م²',
        'cta_book': 'احجز موعد معاينة',
        'cta_whatsapp': 'تواصل عبر واتساب',
        'cta_call': 'اتصل الآن',
        'cta_location': 'موقع المشروع',
        'back_projects': 'كل المشاريع',

        'stats_title': 'نظرة عامة',
        'stats': [
            {'num': '٤',        'label': 'أدوار',      'sub': 'دور كامل لكل عائلة'},
            {'num': '٤',        'label': 'منازل',      'sub': 'شقة واحدة لكل دور'},
            {'num': '١٩٢–١٩٨',  'label': 'م² للشقة',   'sub': 'الأرضي / الأدوار العليا'},
            {'num': '٤',        'label': 'مواقف',      'sub': 'موقف مخصص لكل منزل'},
        ],

        'privacy_kicker': 'الخصوصية',
        'privacy_title_1': 'شقة واحدة.',
        'privacy_title_2': 'دور كامل.',
        'privacy_desc': 'لا تشارك جداراً ولا بسطة درج ولا مصعداً مع عائلة أخرى. تخرج من المصعد فتجد نفسك في منزلك — الدور كله لك.',
        'privacy_points': [
            'لا ممرات مشتركة بين الشقق',
            'نوافذ على الجهات الأربع — دون جيران مقابلين',
            'بهو مصعد خاص يخدم دورك وحده',
        ],

        'floors_kicker': 'اختر دورك',
        'floors_title': 'المنازل الأربعة',
        'floors': [
            {'tag': 'الأرضي', 'name': 'الدور الأرضي', 'area': '١٩٢ م²',
             'config': 'جناح رئيسي + غرفتا نوم + غرفة خادمة',
             'highlight': 'الشقة الوحيدة التي تطل مباشرة على مساحة خضراء خاصة من ثلاث جهات — حديقة ومسطح أخضر خلفي آمن.'},
            {'tag': 'الأول', 'name': 'الدور الأول', 'area': '١٩٨ م²',
             'config': 'جناحا نوم رئيسيان + غرفة + غرفة خادمة',
             'highlight': 'مخطط واسع بجناحين رئيسيين لكل منهما خزانته وحمامه، وغرفة ثالثة، وشرفتان خاصتان.'},
            {'tag': 'الثاني', 'name': 'الدور الثاني', 'area': '١٩٨ م²',
             'config': 'جناحا نوم رئيسيان + غرفة + غرفة خادمة',
             'highlight': 'نفس مخطط الدور الأول المتكامل — جناحان رئيسيان وشرفتان خاصتان وإطلالات مفتوحة.'},
            {'tag': 'الفيلا', 'name': 'الفيلا — الدور الثالث', 'area': '١٩٨ م²',
             'config': 'نفس المخطط + سطح خاص',
             'highlight': 'نفس المساحة السخية مع فارق واحد يغيّر كل شيء: درج داخلي خاص يصعد إلى سطح يخصّك وحدك — حديقة سطح ومجلس تحت النجوم.'},
        ],

        'entrance_kicker': 'التخطيط',
        'entrance_title': 'مدخلان منفصلان. الضيوف لا يعبرون على العائلة.',
        'entrances': [
            {'name': 'مدخل الضيوف',
             'desc': 'يفتح مباشرةً على المجلس وصالة الطعام الرسمية بدورة مياه خاصة للضيوف. يُستقبل الزائر ويُودَّع دون أن يمرّ ببابِ غرفةِ نوم.'},
            {'name': 'مدخل العائلة',
             'desc': 'يقود إلى صالة المعيشة والمطبخ وجناح الغرف. وممرّ خدمة منفصل يربط المطبخ ومنطقة الغسيل وغرفة الخادمة — فلا يمرّ العمل المنزلي عبر مساحة المعيشة.'},
        ],

        'living_kicker': 'أسلوب حياة',
        'living_title': 'منزل يتكيّف مع طريقة عيشك',
        'living': [
            {'icon': 'flex', 'title': 'مساحات مرنة',
             'desc': 'مطبخ مفتوح على الطعام والمعيشة — أو أغلقه بفاصل عند الطبخ الثقيل أو قدوم الضيوف. صالة طعام رسمية تُفتح على أيٍّ من الجانبين، ومنطقة غسيل مستقلة.'},
            {'icon': 'light', 'title': 'إضاءة طبيعية وخصوصية تامة',
             'desc': 'سكاي لايت زجاجي يصبّ الضوء على كامل ارتفاع الدرج والبهو، ومشربيات خشبية تُرشّح الشمس وتحجب النظرات، وفتحات على الجهات الأربع لكل غرفة.'},
            {'icon': 'outdoor', 'title': 'مساحة خارجية لكل منزل',
             'desc': 'شرفتان خاصتان في الأدوار العليا، وحديقة ومسطح أخضر خلفي في الأرضي، وسطح كامل خاص للفيلا يُوصل بدرج داخلي.'},
        ],

        'compare_kicker': 'قارن',
        'compare_title': 'المنازل الأربعة جنباً إلى جنب',
        'compare_head': ['', 'الأرضي', 'الأول', 'الثاني', 'الفيلا'],
        'compare_rows': [
            ['المساحة المبنية', '١٩٢ م²', '١٩٨ م²', '١٩٨ م²', '١٩٨ م²'],
            ['الأجنحة الرئيسية', '١', '٢', '٢', '٢'],
            ['غرف نوم أخرى', '٢', '١', '١', '١'],
            ['غرفة خادمة + دورة مياه', '✓', '✓', '✓', '✓'],
            ['مجلس ضيوف + دورة مياه', '✓', '✓', '✓', '✓'],
            ['مطبخ مفتوح/قابل للإغلاق', '✓', '✓', '✓', '✓'],
            ['شرفات خاصة', '—', '٢', '٢', '٢'],
            ['حديقة ومسطح أخضر', '✓', '—', '—', '—'],
            ['سطح خاص', '—', '—', '—', '✓'],
        ],
        'compare_note': 'تشترك جميع الشقق في المصعد ودرج السكاي لايت وبهو المدخل. موقف واحد لكل منزل.',

        'includes_kicker': 'المواصفات',
        'includes_title': 'ما يشمله كل منزل',
        'includes': [
            '٣ غرف نوم بخزائن مدمجة',
            'غرفة خادمة بدورة مياه خاصة',
            'منطقة غسيل مستقلة',
            'مطبخ واسع مفتوح قابل للإغلاق',
            'مجلس ضيوف بدورة مياه',
            'صالة طعام رسمية مرنة الوصل',
            'صالة معيشة مضاءة مع طعام عائلي',
            'حمامات داخلية للأجنحة الرئيسية',
            'إضاءة طبيعية لكل غرفة',
            'مصعد وبهو مدخل مضاء بسكاي لايت',
            'موقف سيارة مخصص',
            'خصوصية تامة عن الجيران',
        ],

        'plans_kicker': 'المخططات',
        'plans_title': 'مخططات الأدوار',
        'plan_ground_label': 'مخطط الدور الأرضي',
        'plan_upper_label': 'مخطط الأدوار العليا (الأول / الثاني / الثالث)',

        'gallery_kicker': 'المشروع',
        'gallery_title': 'لمحات من العمارة',

        'interiors_kicker': 'التصاميم الداخلية',
        'interiors_title': 'من الداخل',
        'interiors_desc': 'تشطيبات راقية ومساحات مضاءة بذوق عصري في كل ركن من المنزل.',
        'interiors': [
            {'img': 'interior-living.jpg',   'label': 'صالة المعيشة'},
            {'img': 'interior-majlis.jpg',   'label': 'مجلس الضيوف'},
            {'img': 'interior-dining.jpg',   'label': 'صالة الطعام'},
            {'img': 'interior-kitchen.jpg',  'label': 'المطبخ'},
            {'img': 'interior-bedroom.jpg',  'label': 'غرفة النوم الرئيسية'},
            {'img': 'interior-entrance.jpg', 'label': 'المدخل والبهو'},
        ],

        'final_title_1': 'أربعة منازل. أربعة أدوار.',
        'final_title_2': 'أحدها لك.',
        'final_desc': 'لحجز موعد معاينة خاص، تواصل مع مكتب المبيعات.',

        'info_kicker': 'بيانات المشروع',
        'info_title': 'الجهات والاعتمادات',
        'info': [
            ('المالك والمطوّر', 'شركة باء البناء'),
            ('مطوّر عقاري معتمد — رقم الشهادة', '2589077735'),
            ('رخصة رقم', '470621770643'),
            ('المكتب المشرف', 'دليل العمارة للاستشارات الهندسية'),
            ('الهاتف', '0593394747'),
        ],
        'slogan': 'باء البناء … جودة تُبنى عليها الثقة',
    },

    'en': {
        'name': 'Adwar Al Khuzami',
        'name_latin': 'ADWAR AL KHUZAMI',
        'city': 'Madinah',
        'location': 'Madinah — Al Khuzama District',
        'status': 'Available Now',
        'hero_kicker': 'Residential Project · Madinah',
        'hero_tagline_1': 'Four private residences.',
        'hero_tagline_2': 'One address.',
        'hero_desc': 'A boutique residential building in the Al Khuzama district of Madinah — one full-floor apartment per level, each with its own garden, balconies or private roof.',
        'hero_meta': '4 Floors · 4 Homes · 192–198 m²',
        'cta_book': 'Book a Private Viewing',
        'cta_whatsapp': 'Chat on WhatsApp',
        'cta_call': 'Call Now',
        'cta_location': 'Project Location',
        'back_projects': 'All Projects',

        'stats_title': 'At a Glance',
        'stats': [
            {'num': '4',       'label': 'Floors',      'sub': 'One full floor per family'},
            {'num': '4',       'label': 'Homes',       'sub': 'One apartment per floor'},
            {'num': '192–198', 'label': 'm² per home', 'sub': 'Ground / upper floors'},
            {'num': '4',       'label': 'Parking',     'sub': 'One bay per residence'},
        ],

        'privacy_kicker': 'Privacy',
        'privacy_title_1': 'One apartment.',
        'privacy_title_2': 'One entire floor.',
        'privacy_desc': 'You never share a wall, a landing or a lift call with another family. Step out of the lift and you are already home — the whole floor is yours.',
        'privacy_points': [
            'No shared corridors between apartments',
            'Windows on all four sides — no facing neighbours',
            'Private lift lobby serving your floor only',
        ],

        'floors_kicker': 'Choose Your Floor',
        'floors_title': 'The Four Residences',
        'floors': [
            {'tag': 'Ground', 'name': 'Ground Floor Residence', 'area': '192 m²',
             'config': '1 master + 2 bedrooms + maid',
             'highlight': 'The only apartment that opens straight onto private green space on three sides — a garden and a safe rear lawn.'},
            {'tag': 'First', 'name': 'First Floor', 'area': '198 m²',
             'config': '2 masters + 1 bedroom + maid',
             'highlight': 'A generous plan with two master suites — each with its own wardrobe and bathroom — a third bedroom and two private balconies.'},
            {'tag': 'Second', 'name': 'Second Floor', 'area': '198 m²',
             'config': '2 masters + 1 bedroom + maid',
             'highlight': 'The same complete layout as the first floor — two master suites, two private balconies and open views.'},
            {'tag': 'Villa', 'name': 'The Villa — Third Floor', 'area': '198 m²',
             'config': 'Same plan + private roof',
             'highlight': 'The same generous plan with one difference that changes everything: a private internal staircase to a roof that belongs to you alone.'},
        ],

        'entrance_kicker': 'Planning',
        'entrance_title': 'Two entrances. Guests never cross the family.',
        'entrances': [
            {'name': 'Guest Entrance',
             'desc': 'Opens directly into the majlis and formal dining room, with its own guest WC. Visitors are received and seen out without ever passing a bedroom door.'},
            {'name': 'Family Entrance',
             'desc': 'Leads into the living hall, kitchen and bedroom wing. A separate service corridor links the kitchen, laundry and maid\'s room — so housework never runs through the living space.'},
        ],

        'living_kicker': 'A Way of Living',
        'living_title': 'A home that adapts to how you live',
        'living': [
            {'icon': 'flex', 'title': 'Flexible spaces',
             'desc': 'An open kitchen onto the family dining and living area — or add a partition to close it off for heavy cooking or guests. A formal dining room that opens either way, and a dedicated laundry zone.'},
            {'icon': 'light', 'title': 'Daylight everywhere, total privacy',
             'desc': 'A glazed skylight pours daylight down the full height of the stair and lobby, mashrabiya screens filter the sun and block sightlines, and every room reaches an external wall on all four sides.'},
            {'icon': 'outdoor', 'title': 'Every home has its own outside',
             'desc': 'Two private balconies on the upper floors, a garden and rear lawn on the ground floor, and a full private roof for the villa, reached by an internal stair.'},
        ],

        'compare_kicker': 'Compare',
        'compare_title': 'The four residences side by side',
        'compare_head': ['', 'Ground', 'First', 'Second', 'Villa'],
        'compare_rows': [
            ['Built area', '192 m²', '198 m²', '198 m²', '198 m²'],
            ['Master suites', '1', '2', '2', '2'],
            ['Other bedrooms', '2', '1', '1', '1'],
            ['Maid\'s room + toilet', '✓', '✓', '✓', '✓'],
            ['Guest majlis + WC', '✓', '✓', '✓', '✓'],
            ['Open / closable kitchen', '✓', '✓', '✓', '✓'],
            ['Private balconies', '—', '2', '2', '2'],
            ['Garden & rear lawn', '✓', '—', '—', '—'],
            ['Private roof terrace', '—', '—', '—', '✓'],
        ],
        'compare_note': 'All apartments share the lift, the skylit staircase and the entrance lobby. One parking bay per residence.',

        'includes_kicker': 'Specification',
        'includes_title': 'What every home includes',
        'includes': [
            '3 bedrooms with fitted wardrobes',
            'Maid\'s room with its own toilet',
            'Separate laundry area',
            'Large open kitchen, closable',
            'Guest majlis with guest WC',
            'Formal dining, flexibly connected',
            'Well-lit living hall with family dining',
            'En-suite bathrooms to master suites',
            'Natural light to every room',
            'Lift and skylit entrance lobby',
            'One dedicated parking bay',
            'Complete privacy from neighbours',
        ],

        'plans_kicker': 'Floor Plans',
        'plans_title': 'The Floor Layouts',
        'plan_ground_label': 'Ground Floor Plan',
        'plan_upper_label': 'Upper Floors Plan (First / Second / Third)',

        'gallery_kicker': 'The Project',
        'gallery_title': 'Glimpses of the architecture',

        'interiors_kicker': 'Interior Design',
        'interiors_title': 'From the inside',
        'interiors_desc': 'Refined finishes and light-filled spaces with a contemporary taste in every corner of the home.',
        'interiors': [
            {'img': 'interior-living.jpg',   'label': 'Living Hall'},
            {'img': 'interior-majlis.jpg',   'label': 'Guest Majlis'},
            {'img': 'interior-dining.jpg',   'label': 'Dining Room'},
            {'img': 'interior-kitchen.jpg',  'label': 'Kitchen'},
            {'img': 'interior-bedroom.jpg',  'label': 'Master Bedroom'},
            {'img': 'interior-entrance.jpg', 'label': 'Entrance & Lobby'},
        ],

        'final_title_1': 'Four homes. Four floors.',
        'final_title_2': 'One of them is yours.',
        'final_desc': 'To book a private viewing, contact the sales office.',

        'info_kicker': 'Project Details',
        'info_title': 'Authorities & Accreditations',
        'info': [
            ('Owner & Developer', 'Baa Al-Bina Company'),
            ('Accredited developer — Certificate No.', '2589077735'),
            ('License No.', '470621770643'),
            ('Supervising office', 'Daleel Al-Emara Engineering Consultancy'),
            ('Phone', '0593394747'),
        ],
        'slogan': 'Baa Al-Bina … quality you can build trust on',
    },
}

# ملخص المشاريع لصفحة القائمة
def _projects_summary(ctx, lang):
    return [{
        'name':     ctx['khuzami_card_name'],
        'location': ctx['khuzami_card_location'],
        'tagline':  ctx['khuzami_card_tagline'],
        'meta':     ctx['khuzami_card_meta'],
        'status':   ctx['projects_status_now'],
        'url':      reverse('project_khuzami' if lang == 'ar' else 'project_khuzami_en'),
        'cover':    'website/img/projects/khuzami/exterior-hero.jpg',
    }]


def projects_list(request, lang='ar'):
    ctx = _build_ctx(lang, 'projects')
    ctx['projects'] = _projects_summary(ctx, lang)
    return render(request, 'website/projects.html', ctx)


def project_khuzami(request, lang='ar'):
    ctx = _build_ctx(lang, 'project_khuzami')
    p = KHUZAMI[lang]
    ctx['p'] = p
    ctx['map_url'] = KHUZAMI_MAP_URL
    ctx['tel_number'] = '0593394747'
    ctx['page_title'] = p['name'] + ' — ' + ctx['company_name']
    ctx['meta_description'] = p['hero_desc']
    ctx['og_title'] = p['name'] + ' — ' + ctx['company_name']
    ctx['og_description'] = p['hero_desc']
    ctx['og_image_url'] = f"{SITE_BASE}/static/website/img/projects/khuzami/exterior-hero.jpg"
    return render(request, 'website/project-khuzami.html', ctx)


def tree(request):
    return render(request, 'website/tree.html')


def tree_vcard(request):
    vcard = (
        "BEGIN:VCARD\r\n"
        "VERSION:3.0\r\n"
        "N:;شركة باء البناء;;;\r\n"
        "FN:شركة باء البناء\r\n"
        "ORG:شركة باء البناء\r\n"
        "TEL;TYPE=CELL:+966593394747\r\n"
        "EMAIL:b.construction.med@gmail.com\r\n"
        "URL:https://www.bconstructions.org\r\n"
        "END:VCARD\r\n"
    )
    response = HttpResponse(vcard, content_type='text/vcard; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="baa-al-bina.vcf"'
    return response


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
