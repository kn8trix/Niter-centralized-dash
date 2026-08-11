"""Token encryption helpers — Google OAuth credentials at rest.

The Drive/Sheets integration stores OAuth tokens (access + refresh) that must
never sit in the database as plaintext. ``encrypt_secret`` / ``decrypt_secret``
wrap ``cryptography.fernet`` with a key sourced from the
``GOOGLE_TOKEN_ENCRYPTION_KEY`` setting (falling back to a stable SHA-256
derivation of ``SECRET_KEY`` so existing deployments keep working without a
new env var).

``decrypt_secret`` deliberately *falls back to the raw value* when the input is
not a valid Fernet payload — this keeps legacy plaintext rows readable while
every newly written token is encrypted.
"""

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


def _fernet() -> Fernet:
    """Build a Fernet instance from the configured key (or SECRET_KEY-derived)."""
    raw = getattr(settings, 'GOOGLE_TOKEN_ENCRYPTION_KEY', '') or settings.SECRET_KEY or ''
    key = base64.urlsafe_b64encode(hashlib.sha256(raw.encode('utf-8')).digest())
    return Fernet(key)


def encrypt_secret(value):
    """Encrypt ``value`` for storage. Empty/None values pass through unchanged."""
    if not value:
        return value
    return _fernet().encrypt(value.encode('utf-8')).decode('ascii')


def decrypt_secret(value):
    """Decrypt a stored token. Non-Fernet values (legacy plaintext) are returned raw."""
    if not value:
        return value
    try:
        return _fernet().decrypt(value.encode('ascii')).decode('utf-8')
    except (InvalidToken, ValueError, TypeError):
        # Not a Fernet payload — either a legacy plaintext row or a test fixture.
        return value
