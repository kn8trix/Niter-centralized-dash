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
        raise GoogleAccountNotConnected(
            'No Google account connected for this user. '
            'Connect Google in Account Settings first.'
        )
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
