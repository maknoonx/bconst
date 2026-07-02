from django.urls import path
from . import views

urlpatterns = [
    path('',                              views.namadhj_home,       name='namadhj_home'),
    # print
    path('forms/<int:pk>/print/',         views.form_print,         name='form_print'),
    path('letters/<int:pk>/print/',       views.letter_print,       name='letter_print'),
    # forms API
    path('api/forms/create/',             views.form_create,        name='form_create'),
    path('api/forms/<int:pk>/edit/',      views.form_edit,          name='form_edit'),
    path('api/forms/<int:pk>/delete/',    views.form_delete,        name='form_delete'),
    path('api/forms/<int:pk>/',           views.form_detail_json,   name='form_detail_json'),
    # letters API
    path('api/letters/create/',           views.letter_create,      name='letter_create'),
    path('api/letters/<int:pk>/edit/',    views.letter_edit,        name='letter_edit'),
    path('api/letters/<int:pk>/delete/',  views.letter_delete,      name='letter_delete'),
    path('api/letters/<int:pk>/',         views.letter_detail_json, name='letter_detail_json'),
    # categories API
    path('api/form-cats/',                    views.form_cats_list,     name='form_cats_list'),
    path('api/form-cats/create/',             views.form_cat_create,    name='form_cat_create'),
    path('api/form-cats/<int:pk>/edit/',      views.form_cat_edit,      name='form_cat_edit'),
    path('api/form-cats/<int:pk>/delete/',    views.form_cat_delete,    name='form_cat_delete'),
    path('api/letter-cats/',                  views.letter_cats_list,   name='letter_cats_list'),
    path('api/letter-cats/create/',           views.letter_cat_create,  name='letter_cat_create'),
    path('api/letter-cats/<int:pk>/edit/',    views.letter_cat_edit,    name='letter_cat_edit'),
    path('api/letter-cats/<int:pk>/delete/',  views.letter_cat_delete,  name='letter_cat_delete'),
    # employee letters
    path('emp-letters/<str:letter_type>/<int:emp_pk>/print/', views.emp_letter_print, name='emp_letter_print'),
    path('api/employees/<int:pk>/',       views.emp_detail_json,    name='emp_detail_json'),
]
