from django.urls import path

from . import views

urlpatterns = [
    # Gateway server-to-server endpoints (no CSRF / auth).
    path('webhook/bkash/', views.bkash_callback, name='payments_bkash_webhook'),
    path('webhook/nagad/', views.nagad_callback, name='payments_nagad_webhook'),
    # Versioned generic callback — dispatches to the per-gateway handler.
    path('api/v1/payments/callback/<str:gateway>/', views.gateway_callback, name='payments_gateway_callback'),
]
