from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from host.views import medical_admin_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('core.urls')),
    path('medical/admin/', medical_admin_dashboard, name='medical_admin_dashboard'),
    path('host/', include('host.urls')),

    # Authentication
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html',
        redirect_authenticated_user=True,
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
