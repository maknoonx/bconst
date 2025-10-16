from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('employee-login/', views.employee_login, name="employee_login"),
    path('architectural-services/', views.architectural_services, name="architectural_services"),
    path('structural-services/', views.structural_services, name="structural_services"),
    path('design-services/', views.design_services, name="design_services"),
    path('project/<int:project_id>/', views.project_detail, name="project_detail"),
    path('services/', views.home, name="services"),
    path('projects/', views.home, name="projects"),
    path('about/', views.home, name="about"),
    path('contact/', views.home, name="contact"),
    path('jobs/', views.home, name="jobs"),
]