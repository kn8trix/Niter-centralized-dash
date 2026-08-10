"""Real-time notification delivery over Django Channels WebSockets.

Each authenticated user joins the ``user_<user_id>`` channel group, so any
server component (a view, management command, or background task) can push a
new alert to the user's open browser instantly via
:func:`notify_user` or a raw ``channel_layer.group_send``.
"""

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket endpoint streaming notifications to a single logged-in user.

    The consumer authenticates from ``scope['user']`` (populated by
    ``AuthMiddlewareStack``), rejects anonymous connections, and subscribes to
    the ``user_<id>`` group for the lifetime of the socket.

    Server-side push payloads use the event type ``'notification'``:

    .. code-block:: python

        notify_user(user_id, {
            'id': 1,
            'title': 'Midterm schedule updated',
            'message': 'CS101 midterm moved to Aug 20.',
            'category': 'academic',
            'is_read': False,
            'created_at': '2026-08-10T10:00:00',
        })
    """

    async def connect(self):
        user = self.scope.get('user')
        if user is None or not user.is_authenticated:
            await self.close()
            return
        self.group_name = 'user_%s' % user.pk
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if getattr(self, 'group_name', None):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notification(self, event):
        """Relay a pushed notification payload to the browser."""
        await self.send_json(event.get('payload', {}))


def notify_user(user_id, payload):
    """Broadcast ``payload`` to every open socket of ``user_id``.

    Thin sync wrapper around ``group_send`` so any sync view/management
    command can push a real-time alert without touching the channel layer
    directly. Must be called from sync code — inside an async context, await
    ``channel_layer.group_send`` instead.
    """
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(
        'user_%s' % user_id,
        {'type': 'notification', 'payload': payload},
    )
