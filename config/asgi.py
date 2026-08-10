"""ASGI entrypoint — serves HTTP (WSGI-compatible) plus WebSockets.

Routing: HTTP requests go to the standard Django ASGI handler; WebSocket
connections (``/ws/...``) are authenticated via ``AuthMiddlewareStack`` and
dispatched by ``core.routing`` (real-time notification engine).
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Initialize Django before importing anything that touches the ORM.
django_asgi_app = get_asgi_application()

from core.routing import websocket_urlpatterns  # noqa: E402  (needs Django setup)

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns),
    ),
})
