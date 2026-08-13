"""WebSocket routing for the core app (real-time notification engine)."""

from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
    # Patient ↔ doctor consultation chat (persistent, per-thread groups)
    re_path(r'^ws/medical-chat/(?P<thread_id>\d+)/$', consumers.MedicalChatConsumer.as_asgi()),
    # Campus-wide emergency broadcasts (trigger/resolve siren events)
    re_path(r'^ws/emergency/$', consumers.EmergencyConsumer.as_asgi()),
]
