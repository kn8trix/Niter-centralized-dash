"""Google Drive service — academic notes & lecture materials uploads.

Dedicated Drive module for the Academic Notes side of the portal. Uses the
**Drive v3 API** (``googleapiclient.discovery.build('drive', 'v3')``) with the
signed-in user's stored OAuth credentials (``GoogleUserToken``, encrypted at
rest) and uploads files into a dedicated per-user folder named
``NITER Centralized Dash Notes``.

- ``upload_file_to_drive`` uploads a Django ``UploadedFile`` into the notes
  folder and returns ``webViewLink`` + ``webContentLink`` so the caller can
  persist both URLs onto ``UserNote`` / ``CourseMaterial`` rows.
- ``get_drive_storage_info`` reads the account email + storage quota via
  ``drive.about().get`` for the Settings → Google Drive tab (no network call
  in tests — mocked).
- ``get_or_create_notes_folder`` is the folder bootstrap shared by every
  upload path.

All Google/transport failures are surfaced as
:class:`core.google_service.GoogleServiceError` (with the
:class:`GoogleReauthRequired` / :class:`GoogleAccountNotConnected` subtypes)
so the views answer 401 / 500 consistently.
"""

import io

from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from core.google_service import (
    FOLDER_MIME_TYPE,
    GoogleAccountNotConnected,
    GoogleReauthRequired,
    GoogleServiceError,
    get_google_credentials,
)

NOTES_FOLDER_NAME = 'NITER Centralized Dash Notes'


# ---------------------------------------------------------------------------
# Folder bootstrap
# ---------------------------------------------------------------------------
def _find_or_create_folder(drive_service, folder_name):
    """Return the ID of ``folder_name`` (non-trashed), creating it if absent."""
    escaped = folder_name.replace("'", "\\'")
    query = "name='%s' and mimeType='%s' and trashed=false" % (escaped, FOLDER_MIME_TYPE)
    result = drive_service.files().list(
        q=query, spaces='drive', fields='files(id, name)',
    ).execute()
    files = result.get('files', [])
    if files:
        return files[0]['id']
    folder = drive_service.files().create(
        body={'name': folder_name, 'mimeType': FOLDER_MIME_TYPE}, fields='id',
    ).execute()
    return folder['id']


def get_or_create_notes_folder(user, folder_name=NOTES_FOLDER_NAME):
    """Return the Drive folder ID for ``folder_name`` (creating it if absent)."""
    try:
        creds = get_google_credentials(user)
        drive_service = build('drive', 'v3', credentials=creds)
        return _find_or_create_folder(drive_service, folder_name)
    except (GoogleAccountNotConnected, GoogleReauthRequired, GoogleServiceError):
        raise
    except RefreshError as exc:  # lazy refresh during the API call failed
        raise GoogleReauthRequired(
            'Your Google session has expired — reconnect Google to continue.'
        ) from exc
    except Exception as exc:
        raise GoogleServiceError('Could not prepare the notes folder: %s' % exc) from exc


# ---------------------------------------------------------------------------
# Uploads
# ---------------------------------------------------------------------------
def upload_file_to_drive(user, uploaded_file, folder_name=NOTES_FOLDER_NAME):
    """Upload ``uploaded_file`` into the user's notes Drive folder.

    Returns ``{'file_id', 'web_view_link', 'web_content_link'}`` — both the
    view URL (browser) and the direct download URL — so the caller can persist
    them onto ``UserNote`` / ``CourseMaterial`` rows. ``uploaded_file`` is a
    Django ``UploadedFile`` (``.read()`` + ``.name`` + ``.content_type`` are
    used).
    """
    creds = get_google_credentials(user)
    try:
        drive_service = build('drive', 'v3', credentials=creds)
        folder_id = _find_or_create_folder(drive_service, folder_name)

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
            fields='id, webViewLink, webContentLink',
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
        'web_view_link': uploaded.get('webViewLink'),
        'web_content_link': uploaded.get('webContentLink'),
    }


# ---------------------------------------------------------------------------
# Storage info (Settings → Google Drive tab)
# ---------------------------------------------------------------------------
def get_drive_storage_info(user):
    """Return the user's Drive account email + storage quota.

    ``drive.about().get(fields='user, storageQuota')`` requires a Drive scope —
    the configured ``drive.readonly`` scope covers it. Returns a dict with
    ``email``, ``quota_total`` and ``quota_used`` (bytes), or ``None`` when the
    account is not connected / the API call fails (tab renders gracefully).
    """
    try:
        creds = get_google_credentials(user)
        drive_service = build('drive', 'v3', credentials=creds)
        about = drive_service.about().get(fields='user, storageQuota').execute()
        quota = about.get('storageQuota') or {}
        info = {
            'email': (about.get('user') or {}).get('emailAddress', ''),
            'quota_total': int(quota.get('limit') or 0),
            'quota_used': int(quota.get('usage') or 0),
        }
        info['quota_remaining'] = max(0, info['quota_total'] - info['quota_used'])
        return info
    except (GoogleAccountNotConnected, GoogleReauthRequired, GoogleServiceError, RefreshError):
        return None
    except Exception:
        return None
