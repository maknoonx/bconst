from django.urls import path
from . import views

urlpatterns = [
    path('',                                   views.inventory_home,    name='inventory_home'),
    # warehouses
    path('warehouses/create/',                 views.warehouse_create,  name='inv_wh_create'),
    path('warehouses/<int:pk>/edit/',          views.warehouse_edit,    name='inv_wh_edit'),
    path('warehouses/<int:pk>/delete/',        views.warehouse_delete,  name='inv_wh_delete'),
    # item categories
    path('item-cats/create/',                  views.item_cat_create,   name='inv_cat_create'),
    path('item-cats/<int:pk>/delete/',         views.item_cat_delete,   name='inv_cat_delete'),
    # items
    path('items/create/',                      views.item_create,       name='inv_item_create'),
    path('items/<int:pk>/edit/',               views.item_edit,         name='inv_item_edit'),
    path('items/<int:pk>/delete/',             views.item_delete,       name='inv_item_delete'),
    # suppliers
    path('suppliers/create/',                  views.supplier_create,   name='inv_sup_create'),
    path('suppliers/<int:pk>/edit/',           views.supplier_edit,     name='inv_sup_edit'),
    path('suppliers/<int:pk>/delete/',         views.supplier_delete,   name='inv_sup_delete'),
    # purchase orders
    path('po/create/',                         views.po_create,         name='inv_po_create'),
    path('po/<int:pk>/detail/',                views.po_detail_json,    name='inv_po_detail'),
    path('po/<int:pk>/receive/',               views.po_receive,        name='inv_po_receive'),
    path('po/<int:pk>/cancel/',                views.po_cancel,         name='inv_po_cancel'),
    path('po/<int:pk>/delete/',                views.po_delete,         name='inv_po_delete'),
    # movements
    path('movements/create/',                  views.movement_create,   name='inv_mov_create'),
    # alerts
    path('alerts/<int:pk>/resolve/',           views.alert_resolve,     name='inv_alert_resolve'),
]
