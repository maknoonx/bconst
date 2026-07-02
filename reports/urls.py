from django.urls import path
from . import views

urlpatterns = [
    path('',           views.reports_home,      name='reports_home'),
    path('invoices/',  views.report_invoices,   name='report_invoices'),
    path('vat/',       views.report_vat,        name='report_vat'),
    path('revenue/',   views.report_revenue,    name='report_revenue'),
    path('clients/',   views.report_clients,    name='report_clients'),
    path('employees/', views.report_employees,  name='report_employees'),
    path('inventory/', views.report_inventory,  name='report_inventory'),
    path('marketing/', views.report_marketing,  name='report_marketing'),
    path('receipts/',  views.report_receipts,   name='report_receipts'),
    path('financial/', views.report_financial,  name='report_financial'),
]
