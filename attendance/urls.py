from django.urls import path
from . import views

urlpatterns = [
    path('', views.checkin_page, name='attendance_checkin'),
    path('record/create/', views.record_create, name='attendance_record_create'),
    path('<int:pk>/approve/', views.approve_record, name='attendance_approve'),
    path('approve-bulk/', views.approve_bulk, name='attendance_approve_bulk'),
    path('overtime/create/', views.overtime_create, name='overtime_create'),
    path('overtime/<int:pk>/delete/', views.overtime_delete, name='overtime_delete'),
]
