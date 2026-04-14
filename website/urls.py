from django.urls import path
from . import views

urlpatterns = [
    # العربية (الافتراضية)
    path('',          views.home,        {'lang': 'ar'}, name='home'),
    path('studio/',   views.studio,      {'lang': 'ar'}, name='studio'),
    path('coming-soon/', views.coming_soon, {'lang': 'ar'}, name='coming_soon'),

    # الإنجليزية
    path('en/',          views.home,        {'lang': 'en'}, name='home_en'),
    path('en/studio/',   views.studio,      {'lang': 'en'}, name='studio_en'),
    path('en/coming-soon/', views.coming_soon, {'lang': 'en'}, name='coming_soon_en'),
]
