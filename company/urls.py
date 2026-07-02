from django.urls import path
from . import views

urlpatterns = [
    path('', views.company_home, name='company_home'),
    path('save/', views.company_save, name='company_save'),
    path('docs/create/', views.doc_create, name='company_doc_create'),
    path('docs/<int:pk>/delete/', views.doc_delete, name='company_doc_delete'),
    path('pm/create/', views.pm_create, name='company_pm_create'),
    path('pm/<int:pk>/edit/', views.pm_edit, name='company_pm_edit'),
    path('pm/<int:pk>/delete/', views.pm_delete, name='company_pm_delete'),
]
