from django.urls import path
from . import views

urlpatterns = [
    path('', views.marketing_home, name='marketing_home'),
    path('plans/create/', views.plan_create, name='mkt_plan_create'),
    path('plans/<int:pk>/edit/', views.plan_edit, name='mkt_plan_edit'),
    path('plans/<int:pk>/delete/', views.plan_delete, name='mkt_plan_delete'),
    path('plans/<int:pk>/approve/', views.plan_approve, name='mkt_plan_approve'),
    path('plans/<int:pk>/complete/', views.plan_complete, name='mkt_plan_complete'),
    path('marketers/create/', views.marketer_create, name='mkt_marketer_create'),
    path('marketers/<int:pk>/edit/', views.marketer_edit, name='mkt_marketer_edit'),
    path('marketers/<int:pk>/delete/', views.marketer_delete, name='mkt_marketer_delete'),
]
