from django.urls import path
from django.views.generic.base import TemplateView
from . import views

urlpatterns = [
    # العربية (الافتراضية)
    path('',                          views.home,           {'lang': 'ar'}, name='home'),
    path('studio/',                   views.studio,         {'lang': 'ar'}, name='studio'),
    path('coming-soon/',              views.coming_soon,    {'lang': 'ar'}, name='coming_soon'),
    path('contact/',                  views.contact,        {'lang': 'ar'}, name='contact'),
    path('privacy/',                  views.privacy,        {'lang': 'ar'}, name='privacy'),
    path('terms/',                    views.terms,          {'lang': 'ar'}, name='terms'),
    path('services/',                 views.services_list,  {'lang': 'ar'}, name='services'),
    path('services/<slug:slug>/',     views.service_detail, {'lang': 'ar'}, name='service_detail'),

    # Linktree-style page
    path('tree/',                     views.tree,           name='tree'),
    path('tree/vcard/',               views.tree_vcard,      name='tree_vcard'),

    # الإنجليزية
    path('en/',                       views.home,           {'lang': 'en'}, name='home_en'),
    path('en/studio/',                views.studio,         {'lang': 'en'}, name='studio_en'),
    path('en/coming-soon/',           views.coming_soon,    {'lang': 'en'}, name='coming_soon_en'),
    path('en/contact/',               views.contact,        {'lang': 'en'}, name='contact_en'),
    path('en/privacy/',               views.privacy,        {'lang': 'en'}, name='privacy_en'),
    path('en/terms/',                 views.terms,          {'lang': 'en'}, name='terms_en'),
    path('en/services/',              views.services_list,  {'lang': 'en'}, name='services_en'),
    path('en/services/<slug:slug>/',  views.service_detail, {'lang': 'en'}, name='service_detail_en'),
]

urlpatterns += [
    path('robots.txt', TemplateView.as_view(template_name='website/robots.txt', content_type='text/plain')),
    path('sitemap.xml', TemplateView.as_view(template_name='website/sitemap.xml', content_type='application/xml')),
]
