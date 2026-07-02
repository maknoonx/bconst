from django.urls import path
from . import views

urlpatterns = [
    path('',                                views.employee_list,          name='employee_list'),
    path('create/',                         views.employee_create,        name='employee_create'),
    path('<int:pk>/',                       views.employee_detail,        name='employee_detail'),
    path('<int:pk>/edit/',                  views.employee_edit,          name='employee_edit'),
    path('<int:pk>/delete/',               views.employee_delete,        name='employee_delete'),
    path('<int:pk>/toggle/',               views.employee_toggle_status, name='employee_toggle'),

    path('users/create/',                  views.user_create,            name='user_create'),
    path('users/<int:pk>/edit/',           views.user_edit,              name='user_edit'),
    path('users/<int:pk>/delete/',         views.user_delete,            name='user_delete'),
    path('users/<int:pk>/resend-email/',   views.user_resend_email,      name='user_resend_email'),

    path('groups/create/',                 views.group_create,           name='group_create'),
    path('groups/<int:pk>/',               views.group_detail,           name='group_detail'),
    path('groups/<int:pk>/edit/',          views.group_edit,             name='group_edit'),
    path('groups/<int:pk>/delete/',        views.group_delete,           name='group_delete'),

    path('set-password/<uidb64>/<token>/', views.set_password,           name='set_password'),
]
