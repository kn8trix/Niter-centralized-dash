from django.urls import path
from . import views

app_name = 'host'

urlpatterns = [
    path('', views.index, name='index'),
    path('medical/', views.medical_host_dashboard, name='medical_host_dashboard'),

    # Pharmacy Inventory Management
    path('medical/pharmacy/inventory/', views.pharmacy_inventory, name='pharmacy_inventory'),
    path('medical/pharmacy/inventory/add/', views.pharmacy_product_add, name='pharmacy_product_add'),
    path('medical/pharmacy/inventory/<int:pk>/edit/', views.pharmacy_product_edit, name='pharmacy_product_edit'),
    path('medical/pharmacy/inventory/<int:pk>/delete/', views.pharmacy_product_delete, name='pharmacy_product_delete'),
    path('medical/pharmacy/inventory/<int:pk>/toggle/', views.pharmacy_stock_toggle, name='pharmacy_stock_toggle'),
    path('medical/pharmacy/inventory/<int:pk>/adjust/', views.pharmacy_stock_adjust, name='pharmacy_stock_adjust'),
]
