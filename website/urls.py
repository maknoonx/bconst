from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('employee-login/', views.home, name="employee_login"),  # You can create separate view later
    path('services/', views.home, name="services"),  # You can create separate view later
    path('projects/', views.home, name="projects"),  # You can create separate view later
    path('about/', views.home, name="about"),  # You can create separate view later
    path('contact/', views.home, name="contact"),  # You can create separate view later
    path('jobs/', views.home, name="jobs"),  # You can create separate view later
]