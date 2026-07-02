from django.urls import path
from . import views

urlpatterns = [
    path('',                              views.dashboard,      name='projects_dashboard'),
    path('list/',                         views.project_list,   name='project_list'),
    path('create/',                       views.project_create, name='project_create'),
    path('<int:pk>/',                     views.project_detail, name='project_detail'),
    path('<int:pk>/edit/',                views.project_edit,   name='project_edit'),
    path('<int:pk>/delete/',              views.project_delete, name='project_delete'),
    path('<int:pk>/task/create/',         views.task_create,    name='task_create'),
    path('<int:pk>/task/<int:task_pk>/delete/', views.task_delete, name='task_delete'),
    path('<int:pk>/task/<int:task_pk>/toggle/', views.task_toggle, name='task_toggle'),
    # standalone tasks management
    path('tasks/',                        views.task_list,         name='task_list'),
    path('tasks/create/',                 views.task_list_create,  name='task_list_create'),
    path('tasks/<int:pk>/',              views.task_list_detail,  name='task_list_detail'),
    path('tasks/<int:pk>/edit/',         views.task_list_edit,    name='task_list_edit'),
    path('tasks/<int:pk>/delete/',       views.task_list_delete,  name='task_list_delete'),
]
