"""Google service layer — Drive notes upload + Sheets club data (Phase 3).

Thin wrappers over ``google-api-python-client`` and ``gspread`` that rebuild
each user's stored OAuth credentials (``GoogleUserToken``) and expose:

- ``get_google_credentials(user)``            -> ``Credentials``
- ``upload_note_to_user_drive(...)``          -> ``{'file_id', 'web_link'}``
- ``get_club_sheet_data(sheet_url, user)``    -> list of row dicts
- ``append_club_sheet_row(sheet_url, row_data, user)``

Missing tokens and underlying Google API failures are both surfaced as
:class:`GoogleServiceError` so callers can catch a single exception type.
"""

import io

import gspread
from django.utils import timezone
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from .models import GoogleUserToken

FOLDER_MIME_TYPE = 'application/vnd.google-apps.folder'
DEFAULT_FOLDER_NAME = 'CampusDash Notes'


class GoogleServiceError(Exception):
    """Raised when a Google credential lookup or API call fails."""


class GoogleAccountNotConnected(GoogleServiceError):
    """Raised when the user has no stored Google token to build credentials from.

    Kept as its own type so views can answer 401 (client needs to connect
    Google) instead of 500 (server-side API failure).
    """


class GoogleReauthRequired(GoogleServiceError):
    """Raised when a stored token exists but can no longer be refreshed.

    Covers expired tokens with no refresh token and ``RefreshError`` failures
    (revoked access, bad refresh token, network failure during refresh). Views
    translate this into a 401 ``auth_required`` response that points the client
    back at the Google OAuth re-consent flow.
    """


# ---------------------------------------------------------------------------
# 1. Credential reconstruction
# ---------------------------------------------------------------------------
def get_google_credentials(user):
    """Rebuild a valid ``google.oauth2.credentials.Credentials`` object.

    The object carries the stored refresh token, so the transports used by
    googleapiclient / gspread can transparently refresh expired access tokens
    on the user's behalf.

    If the stored access token has already expired and a refresh token is
    available, the token is refreshed here and the newly issued ``access_token``
    + ``expiry`` are persisted back to the user's ``GoogleUserToken`` (Phase 6).
    """
    token = GoogleUserToken.objects.filter(user=user).first()
    if token is None:
        # No legacy row (e.g. the user connected via allauth after the Drive
        # scopes were enabled) — fall back to the allauth SocialToken path,
        # which also mirrors a fresh GoogleUserToken row for future calls.
        return get_user_google_credentials(user)
    creds = Credentials(
        token=token.access_token,
        refresh_token=token.refresh_token,
        token_uri=token.token_uri,
        client_id=token.client_id,
        client_secret=token.client_secret,
        scopes=token.scopes,
        # Lets google-auth refresh proactively instead of waiting for a 401.
        expiry=token.expiry,
    )

    # Expiry check goes through the model (``timezone.now()``) rather than
    # ``creds.expired``: google-auth compares a naive stored expiry against
    # naive UTC, while this project stores naive *local* time (USE_TZ=False),
    # which would make valid future tokens look expired on non-UTC hosts.
    if not token.is_expired:
        return creds

    if not creds.refresh_token:
        # Nothing to refresh with — the user must re-consent.
        raise GoogleReauthRequired(
            'Your Google session has expired. Connect Google again to continue.'
        )

    # Proactively refresh the expired access token and persist the result so
    # the DB copy stays valid for as long as possible.
    try:
        creds.refresh(GoogleAuthRequest())
    except RefreshError as exc:
        raise GoogleReauthRequired(
            'Your Google session has expired or was revoked. '
            'Connect Google again to continue.'
        ) from exc

    token.access_token = creds.token
    # google-auth normally hands back an aware UTC expiry — normalize it to the
    # project's stored convention (local time) so ``is_expired`` keeps comparing
    # like with like. Some callers (tests, offline flows) leave ``creds.expiry``
    # as a naive local datetime; ``localtime()`` would raise ``ValueError`` on
    # those, so store naive values untouched.
    if timezone.is_aware(creds.expiry):
        token.expiry = timezone.localtime(creds.expiry)
    else:
        token.expiry = creds.expiry
    token.save(update_fields=['access_token', 'expiry'])
    return creds


# ---------------------------------------------------------------------------
# 1b. allauth SocialToken credential reconstruction (Drive API access)
# ---------------------------------------------------------------------------
def _configured_google_scopes():
    """Return the Google OAuth scopes configured in ``SOCIALACCOUNT_PROVIDERS``."""
    from django.conf import settings as django_settings
    return list(
        django_settings.SOCIALACCOUNT_PROVIDERS.get('google', {})
        .get('SCOPE', [])
    )


def _get_user_google_social_token(user):
    """Return the user's active allauth ``SocialToken`` for Google, or None."""
    try:
        from allauth.socialaccount.models import SocialAccount, SocialToken
    except Exception:  # allauth not installed / not migrated
        return None
    account = SocialAccount.objects.filter(user=user, provider='google').first()
    if account is None:
        return None
    return SocialToken.objects.filter(account=account).order_by('-id').first()


def _persist_google_user_token(user, social_token, creds):
    """Mirror the allauth token into ``GoogleUserToken`` (legacy storage).

    The Drive/Sheets service layer reads ``GoogleUserToken``; keeping it in
    sync here means the old code paths keep working once a user has completed
    the allauth OAuth flow, without double maintenance.
    """
    app = social_token.app
    if timezone.is_aware(creds.expiry):
        expiry = timezone.localtime(creds.expiry)
    else:
        expiry = creds.expiry
    GoogleUserToken.objects.update_or_create(
        user=user,
        defaults={
            'access_token': creds.token or '',
            'refresh_token': creds.refresh_token or social_token.token_secret or '',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'client_id': getattr(app, 'client_id', '') or '',
            'client_secret': getattr(app, 'secret', '') or '',
            'scopes': _configured_google_scopes(),
            'expiry': expiry or timezone.now(),
        },
    )


def get_user_google_credentials(user):
    """Rebuild valid Google ``Credentials`` from the user's allauth token.

    Looks up the user's active ``SocialToken`` (django-allauth) for Google and
    reconstructs a ``google.oauth2.credentials.Credentials`` object carrying the
    stored refresh token, so the transports used by googleapiclient / gspread
    can transparently refresh expired access tokens.

    If the stored access token has already expired, the token is refreshed here
    using the refresh token (``SocialToken.token_secret``), and the freshly
    issued ``access_token`` + ``expiry`` are persisted back to both the allauth
    ``SocialToken`` and the legacy ``GoogleUserToken`` row.

    Raises :class:`GoogleAccountNotConnected` when the user has no Google
    connection, and :class:`GoogleReauthRequired` when the stored token can no
    longer be refreshed.
    """
    social_token = _get_user_google_social_token(user)
    if social_token is None or not social_token.token:
        raise GoogleAccountNotConnected(
            'No Google account connected for this user. '
            'Connect Google in Account Settings first.'
        )

    app = social_token.app
    creds = Credentials(
        token=social_token.token,
        refresh_token=social_token.token_secret or None,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=getattr(app, 'client_id', '') or '',
        client_secret=getattr(app, 'secret', '') or '',
        scopes=_configured_google_scopes(),
        # Lets google-auth refresh proactively instead of waiting for a 401.
        expiry=social_token.expires_at,
    )

    # Expired? Refresh with the refresh token before any API request. allauth
    # stores naive local expiry (USE_TZ=False) so compare like with like.
    if social_token.expires_at is None or social_token.expires_at <= timezone.now():
        if not creds.refresh_token:
            raise GoogleReauthRequired(
                'Your Google session has expired. Connect Google again to continue.'
            )
        try:
            creds.refresh(GoogleAuthRequest())
        except RefreshError as exc:
            raise GoogleReauthRequired(
                'Your Google session has expired or was revoked. '
                'Connect Google again to continue.'
            ) from exc

        # Persist the refreshed access token + expiry back to allauth storage.
        if timezone.is_aware(creds.expiry):
            social_token.expires_at = timezone.localtime(creds.expiry)
        else:
            social_token.expires_at = creds.expiry
        social_token.token = creds.token
        social_token.save(update_fields=['token', 'expires_at'])

    _persist_google_user_token(user, social_token, creds)
    return creds


def user_has_drive_access(user):
    """Return True when the user holds a valid Google Drive-enabled token.

    Cheap check (no network calls) used by the Account & Google settings tab:
    the user is connected and their stored scopes include a Drive scope, so a
    Drive upload / export would succeed. Mirrored ``GoogleUserToken`` rows are
    also honoured for legacy users.
    """
    drive_scopes = {
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.readonly',
    }
    configured = set(_configured_google_scopes())
    if not (configured & drive_scopes):
        return False

    social_token = _get_user_google_social_token(user)
    if social_token is not None and social_token.token:
        # Valid unless the token is expired with no refresh token left.
        if social_token.expires_at is None or social_token.expires_at > timezone.now():
            return True
        return bool(social_token.token_secret)

    legacy = GoogleUserToken.objects.filter(user=user).first()
    if not (legacy and legacy.access_token):
        return False
    # Valid now, or expired but still refreshable (matches the social path).
    return not legacy.is_expired or bool(legacy.refresh_token)


# ---------------------------------------------------------------------------
# 2. Google Drive notes upload
# ---------------------------------------------------------------------------
def _get_or_create_drive_folder(drive_service, folder_name):
    """Return the ID of the named (non-trashed) Drive folder, creating it if absent."""
    escaped = folder_name.replace("'", "\\'")
    query = "name='%s' and mimeType='%s' and trashed=false" % (escaped, FOLDER_MIME_TYPE)
    result = drive_service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name)',
    ).execute()
    files = result.get('files', [])
    if files:
        return files[0]['id']

    folder = drive_service.files().create(
        body={'name': folder_name, 'mimeType': FOLDER_MIME_TYPE},
        fields='id',
    ).execute()
    return folder['id']


def upload_note_to_user_drive(user, uploaded_file, folder_name=DEFAULT_FOLDER_NAME):
    """Upload ``uploaded_file`` into the user's ``folder_name`` Drive folder.

    Returns ``{'file_id': ..., 'web_link': ...}`` (the file's ``webViewLink``).
    ``uploaded_file`` is a Django ``UploadedFile`` (``.read()`` + ``.name`` +
    ``.content_type`` are used).
    """
    creds = get_google_credentials(user)
    try:
        drive_service = build('drive', 'v3', credentials=creds)
        folder_id = _get_or_create_drive_folder(drive_service, folder_name)

        media = MediaIoBaseUpload(
            io.BytesIO(uploaded_file.read()),
            mimetype=getattr(uploaded_file, 'content_type', None) or 'application/octet-stream',
            resumable=False,
        )
        uploaded = drive_service.files().create(
            body={
                'name': uploaded_file.name or 'note.txt',
                'parents': [folder_id],
            },
            media_body=media,
            fields='id, webViewLink',
        ).execute()
    except RefreshError as exc:  # lazy refresh during the API call failed
        raise GoogleReauthRequired(
            'Your Google session has expired — reconnect Google to continue.'
        ) from exc
    except GoogleServiceError:
        raise
    except Exception as exc:  # HttpError, socket errors, ... -> single catchable type
        raise GoogleServiceError('Google Drive upload failed: %s' % exc) from exc

    return {
        'file_id': uploaded.get('id'),
        'web_link': uploaded.get('webViewLink'),
    }


# ---------------------------------------------------------------------------
# 3. Google Sheets service layer for clubs
# ---------------------------------------------------------------------------
def _first_worksheet(spreadsheet):
    """gspread 6.x dropped the ``sheet1`` shortcut — keep both working."""
    sheet1 = getattr(spreadsheet, 'sheet1', None)
    return sheet1 if sheet1 is not None else spreadsheet.get_worksheet(0)


def _get_gspread_client(user):
    return gspread.authorize(get_google_credentials(user))


def get_club_sheet_data(sheet_url, user):
    """Return every row of the club sheet, keyed by its header row."""
    try:
        client = _get_gspread_client(user)
        worksheet = _first_worksheet(client.open_by_url(sheet_url))
        return worksheet.get_all_records()
    except RefreshError as exc:  # lazy refresh during the API call failed
        raise GoogleReauthRequired(
            'Your Google session has expired — reconnect Google to continue.'
        ) from exc
    except GoogleServiceError:
        raise
    except Exception as exc:
        raise GoogleServiceError('Could not read Google Sheet: %s' % exc) from exc


def append_club_sheet_row(sheet_url, row_data, user):
    """Append ``row_data`` (a list of cell values) to the club sheet."""
    try:
        client = _get_gspread_client(user)
        worksheet = _first_worksheet(client.open_by_url(sheet_url))
        worksheet.append_row(row_data)
    except RefreshError as exc:  # lazy refresh during the API call failed
        raise GoogleReauthRequired(
            'Your Google session has expired — reconnect Google to continue.'
        ) from exc
    except GoogleServiceError:
        raise
    except Exception as exc:
        raise GoogleServiceError('Could not append to Google Sheet: %s' % exc) from exc


def verify_club_transaction(sheet_url, trx_id, user, new_status='Verified'):
    """Mark the sheet row matching ``trx_id`` as ``new_status`` in place.

    Locates the header columns for the transaction id and status, finds the
    physical row whose transaction id matches (case-insensitive, via
    ``gspread``'s own ``find``), and overwrites its status cell. Returns the
    matched row as a header-keyed dict so the caller can notify the student
    it belongs to.

    Raises :class:`GoogleServiceError` when the sheet is missing the required
    columns, no row matches ``trx_id``, or the Google API call itself fails.
    """
    try:
        client = _get_gspread_client(user)
        worksheet = _first_worksheet(client.open_by_url(sheet_url))
        headers = worksheet.row_values(1)
    except RefreshError as exc:  # lazy refresh during the API call failed
        raise GoogleReauthRequired(
            'Your Google session has expired — reconnect Google to continue.'
        ) from exc
    except GoogleServiceError:
        raise
    except Exception as exc:
        raise GoogleServiceError('Could not read the Google Sheet: %s' % exc) from exc

    trx_col = next(
        (index for index, header in enumerate(headers)
         if 'trx' in header.lower() or 'transaction' in header.lower() or header.lower() in ('id', 'trxid')),
        None,
    )
    status_col = next(
        (index for index, header in enumerate(headers) if 'status' in header.lower()),
        None,
    )
    if trx_col is None or status_col is None:
        raise GoogleServiceError(
            'The sheet needs TrxID and Status columns to verify payments.'
        )

    try:
        cell = worksheet.find(str(trx_id).strip(), in_column=trx_col + 1)
    except gspread.exceptions.CellNotFound:
        raise GoogleServiceError('No transaction with TrxID %s found in the sheet.' % trx_id)
    except Exception as exc:  # any other gspread/API failure
        raise GoogleServiceError('Could not search the Google Sheet: %s' % exc) from exc

    try:
        worksheet.update_cell(cell.row, status_col + 1, new_status)
    except Exception as exc:
        raise GoogleServiceError('Could not update the Google Sheet: %s' % exc) from exc

    # Re-read the verified row as a header-keyed dict for the caller.
    values = worksheet.row_values(cell.row)
    return {header: values[index] if index < len(values) else '' for index, header in enumerate(headers)}
