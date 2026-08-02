from django.urls import path
from . import views

urlpatterns = [
    path('',        views.dashboard_home,   name='dashboard_home'),
    path('login/',  views.employee_login,   name='employee_login'),
    path('logout/', views.employee_logout,  name='employee_logout'),
]
