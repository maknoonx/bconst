from django.urls import path
from . import views

urlpatterns = [
    path('', views.accounting_home, name='accounting_home'),
    path('accounts/create/', views.account_create, name='acc_account_create'),
    path('accounts/<int:pk>/edit/', views.account_edit, name='acc_account_edit'),
    path('accounts/<int:pk>/delete/', views.account_delete, name='acc_account_delete'),
    path('journals/create/', views.journal_create, name='acc_journal_create'),
    path('journals/<int:pk>/', views.journal_detail, name='acc_journal_detail'),
    path('journals/<int:pk>/post/', views.journal_post, name='acc_journal_post'),
    path('journals/<int:pk>/delete/', views.journal_delete, name='acc_journal_delete'),
    path('assets/create/', views.asset_create, name='acc_asset_create'),
    path('assets/<int:pk>/edit/', views.asset_edit, name='acc_asset_edit'),
    path('assets/<int:pk>/delete/', views.asset_delete, name='acc_asset_delete'),
    path('payrolls/create/', views.payroll_create, name='acc_payroll_create'),
    path('payrolls/<int:pk>/', views.payroll_detail, name='acc_payroll_detail'),
    path('payrolls/<int:pk>/post/', views.payroll_post, name='acc_payroll_post'),
    path('periods/create/', views.period_create, name='acc_period_create'),
    path('periods/<int:pk>/toggle/', views.period_toggle, name='acc_period_toggle'),
]
