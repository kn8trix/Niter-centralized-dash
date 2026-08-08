from django.urls import path, include
from host.views import medical_admin_dashboard

urlpatterns = [
    path('', include('core.urls')),
    path('medical/admin/', medical_admin_dashboard, name='medical_admin_dashboard'),
    path('host/', include('host.urls')),
]
