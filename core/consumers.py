"""Real-time notification delivery over Django Channels WebSockets.

Each authenticated user joins the ``user_<user_id>`` channel group, so any
server component (a view, management command, or background task) can push a
new alert to the user's open browser instantly via
:func:`notify_user` or a raw ``channel_layer.group_send``.

Resilience: ``notify_user`` never raises. When the configured channel layer
(e.g. a Redis-backed one) is unreachable, the push is skipped and the
notification is simply picked up on the student's next ``fetch_notifications``
poll — a live-push outage must never fail the request that produced the alert.
"""

import logging

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer
from django.utils import timezone

from .models import MedicalChatMessage, MedicalChatThread

logger = logging.getLogger(__name__)


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
    try:
        async_to_sync(channel_layer.group_send)(
            'user_%s' % user_id,
            {'type': 'notification', 'payload': payload},
        )
    except Exception:
        # Channel layer outage (e.g. Redis went down after startup) — log and
        # degrade to poll-only delivery instead of bubbling up a 500.
        logger.warning('notify_user: channel layer push failed for user %s', user_id, exc_info=True)


class EmergencyConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket endpoint streaming campus-wide emergency broadcasts.

    Endpoint: ``ws/emergency/``. Authenticated users join the global
    ``emergency_alerts`` group, so the moment an admin triggers or resolves an
    alert every open dashboard tab updates without a poll. Payloads use the
    event type ``'emergency'`` and carry the full alert object (see
    ``broadcast_emergency``) — the browser renders the banner, overlay and
    siren from that payload.

    Anonymous connections are rejected; staff and students alike subscribe
    (the trigger/resolve actions themselves stay admin-only at the API layer).
    """

    async def connect(self):
        user = self.scope.get('user')
        if user is None or not user.is_authenticated:
            await self.close()
            return
        self.group_name = 'emergency_alerts'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if getattr(self, 'group_name', None):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def emergency(self, event):
        """Relay an emergency broadcast payload to every open tab."""
        await self.send_json(event.get('payload', {}))


def broadcast_emergency(payload):
    """Broadcast an emergency event to every connected dashboard tab.

    Mirrors ``notify_user``'s resilience: the channel layer may be absent or
    unreachable (no Redis / plain WSGI), in which case clients pick the alert
    up on their next ``/api/emergency/active/`` poll. Never raises.
    """
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    try:
        async_to_sync(channel_layer.group_send)(
            'emergency_alerts',
            {'type': 'emergency', 'payload': payload},
        )
    except Exception:
        logger.warning('broadcast_emergency: channel layer push failed', exc_info=True)


class MedicalChatConsumer(AsyncJsonWebsocketConsumer):
    """Persistent patient ↔ doctor consultation chat over WebSockets.

    Endpoint: ``ws/medical-chat/<thread_id>/``. Membership is enforced on
    connect — the thread's patient or any staff member may join. Incoming
    ``{type: "message", content: "..."}`` frames are persisted to
    ``MedicalChatMessage`` and broadcast to the thread's
    ``medical_chat_<id>`` channel group so both sides update live.
    """

    async def connect(self):
        user = self.scope.get('user')
        if user is None or not user.is_authenticated:
            await self.close()
            return
        thread_id = self.scope['url_route']['kwargs'].get('thread_id')
        thread = await database_sync_to_async(self._load_thread)(thread_id, user)
        if thread is None:
            await self.close()
            return
        self.thread_id = thread.pk
        self.group_name = 'medical_chat_%s' % self.thread_id
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    def _load_thread(self, thread_id, user):
        """Return the thread if the user may view it, else None."""
        try:
            thread = MedicalChatThread.objects.get(pk=thread_id)
        except (MedicalChatThread.DoesNotExist, ValueError, TypeError):
            return None
        if not (user.is_staff or thread.patient_id == user.pk):
            return None
        return thread

    async def disconnect(self, close_code):
        if getattr(self, 'group_name', None):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        if content.get('type') != 'message':
            return
        text = str(content.get('content') or '').strip()
        if not text:
            return
        user = self.scope['user']
        message = await database_sync_to_async(self._save_message)(user, text)
        await self.channel_layer.group_send(self.group_name, {
            'type': 'chat.message',
            'payload': {
                'id': message.pk,
                'sender_id': message.sender_id,
                'sender_name': user.get_full_name() or user.username,
                'content': message.content,
                'created_at': message.created_at.strftime('%Y-%m-%d %H:%M'),
            },
        })

    def _save_message(self, user, text):
        """Persist a message row and bump the thread's activity timestamp."""
        message = MedicalChatMessage.objects.create(
            thread_id=self.thread_id, sender=user, content=text,
        )
        MedicalChatThread.objects.filter(pk=self.thread_id).update(
            updated_at=timezone.now(),
        )
        return message

    async def chat_message(self, event):
        """Relay a chat payload to every socket in the thread's group."""
        await self.send_json(event['payload'])


def send_chat_push(thread_id, payload):
    """Broadcast ``payload`` to every socket on a thread's channel group.

    Sync wrapper used by the POST fallback endpoint so a message sent without
    WebSockets still reaches open chat windows. Mirrors ``notify_user``'s
    resilience: channel-layer failures are logged, never raised.
    """
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    try:
        async_to_sync(channel_layer.group_send)(
            'medical_chat_%s' % thread_id,
            {'type': 'chat.message', 'payload': payload},
        )
    except Exception:
        logger.warning('send_chat_push: channel layer push failed for thread %s', thread_id, exc_info=True)
