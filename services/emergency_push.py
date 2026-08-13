"""Emergency alert mobile push (firebase-admin, lazily integrated).

Triggers for every emergency broadcast try to fan out a high-priority
push notification to the mobile app. The integration is *opt-in* and
fails soft by design:

  * ``firebase_admin`` is imported lazily — the package may be absent from
    the environment and nothing breaks (the portal is fully functional
    without mobile push).
  * Credentials come from the ``FIREBASE_CREDENTIALS`` environment variable
    (either the inline JSON of a service-account file or a path to one). When
    it is unset, ``send_emergency_push`` returns ``(0, reason)`` without
    touching the network.
  * Any runtime error (invalid credentials, quota, transport) is logged and
    swallowed — an emergency alert must never 500 because the push channel
    failed; the in-app banner + WebSocket + polling still deliver it.

The Android app (``mobile-webview``) receives the payload with
``data.type = EMERGENCY_ALERT`` and a critical-sound hint, so it can bypass
silent-mode / vibrate / ring regardless of notification settings.
"""

import json
import logging

from django.conf import settings

logger = logging.getLogger('services.emergency_push')

# High-priority critical-channel hint used by the Android app.
EMERGENCY_DATA = {
    'type': 'EMERGENCY_ALERT',
    'sound': 'emergency_siren.wav',
}

# Cache the initialized app handle (only one credentials file per process).
_app_handle = None
_app_initialized = False


def _firebase_app():
    """Return the initialized firebase_admin App, or ``None`` when unconfigured."""
    global _app_handle, _app_initialized
    if _app_initialized:
        return _app_handle

    _app_initialized = True
    creds = getattr(settings, 'FIREBASE_CREDENTIALS', '')
    if not creds:
        return None
    try:
        import firebase_admin
        from firebase_admin import credentials
    except ImportError:
        logger.warning('firebase_admin is not installed — mobile push disabled')
        return None

    try:
        if creds.lstrip().startswith('{'):
            _creds = credentials.Certificate(json.loads(creds))
        else:
            _creds = credentials.Certificate(creds)
        _app_handle = firebase_admin.initialize_app(_creds)
    except Exception:
        logger.exception('Failed to initialize Firebase — mobile push disabled')
        _app_handle = None
    return _app_handle


def send_emergency_push(alert):
    """Send a high-priority push notification for ``alert`` to all FCM tokens.

    Returns a ``(sent, reason)`` tuple — ``sent`` is the number of devices
    messaged, ``reason`` describes why nothing was sent ('' on success).
    Never raises.
    """
    app = _firebase_app()
    if app is None:
        return (0, 'Firebase not configured (set FIREBASE_CREDENTIALS)')

    try:
        import firebase_admin.messaging as messaging
    except ImportError:
        return (0, 'firebase_admin.messaging unavailable')

    # App-instance tokens are looked up from the firestore/RTDB by the mobile
    # app team; with no token registry in this repo we broadcast via topics.
    # Topic messaging lets the Android app subscribe on first launch without
    # any per-device token management on the server.
    message = messaging.Message(
        notification=messaging.Notification(
            title='🚨 EMERGENCY ALERT: %s' % alert.title,
            body=alert.message,
        ),
        data=dict(EMERGENCY_DATA, severity=alert.severity_level or 'WARNING'),
        android=messaging.AndroidConfig(
            priority='high',
            notification=messaging.AndroidNotification(
                channel_id='emergency_alerts',
                sound='emergency_siren.wav',
                default_sound=False,
            ),
        ),
        apns=messaging.APNSConfig(
            headers={'apns-priority': '10', 'apns-push-type': 'alert'},
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    sound='emergency_siren.wav',
                    badge=1,
                    content_available=True,
                ),
            ),
        ),
        topic='emergency_alerts',
    )
    try:
        response = messaging.send(message, app=app)
        logger.info('Emergency push sent: %s', response)
        return (1, '')
    except Exception:
        logger.exception('Emergency push failed for alert %s', alert.pk)
        return (0, 'FCM send failed')
