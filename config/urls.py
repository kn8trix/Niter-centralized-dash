from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from core.views import RoleAwareLoginView
from host.views import medical_admin_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('core.urls')),
    path('medical/admin/', medical_admin_dashboard, name='medical_admin_dashboard'),
    path('host/', include('host.urls')),

    # bKash / Nagad payment webhooks (server-to-server)
    path('payments/', include('payments.urls')),

    # Authentication
    path('login/', RoleAwareLoginView.as_view(
        template_name='login.html',
        redirect_authenticated_user=True,
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

# Serve uploaded course materials (MEDIA_ROOT) in every environment.
# Static assets are handled by WhiteNoise; media is small (PDFs, banners) and
# served directly by Django — swap for django-storages/CDN if media grows.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

