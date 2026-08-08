from django.urls import path
from . import views

app_name = 'host'

urlpatterns = [
    path('', views.index, name='index'),
    path('medical/', views.medical_host_dashboard, name='medical_host_dashboard'),
]
