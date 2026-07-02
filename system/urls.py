from django.urls import path
from . import views

urlpatterns = [
    path('',        views.employee_login,  name='employee_login'),
    path('dashboard/', views.system_dashboard, name='system_dashboard'),
    path('logout/',    views.employee_logout,  name='employee_logout'),
]
