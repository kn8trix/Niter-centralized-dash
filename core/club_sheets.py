"""Club Google Sheets data layer — members, event registrations, club notices.

High-level read/write helpers built on the **Sheets v4 API**
(``googleapiclient.discovery.build('sheets', 'v4')``) with the calling user's
stored OAuth credentials (``GoogleUserToken`` — encrypted at rest, decrypted on
read by ``core.google_service``).

- References accept either a full ``docs.google.com/spreadsheets/d/…`` URL or a
  bare Sheet ID — both are normalized transparently.
- Datasets map to worksheet tabs by name (Members / Registrations / Notices);
  when the named tab is missing, the first worksheet is used, so a single-tab
  sheet keeps working unchanged.
- ``verify_and_setup_sheet`` opens a spreadsheet, creates the default tabs when
  missing, and writes the default column headers into empty tabs — the
  "Verify & Connect Sheet" action from Settings → Club Google Sheets.

All Google/API failures surface as :class:`core.google_service.GoogleServiceError`
(with the :class:`GoogleReauthRequired` / :class:`GoogleAccountNotConnected`
subtypes), so views can answer 401 (re-connect Google) or 500 accordingly.
"""

import re

from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .google_service import (
    GoogleAccountNotConnected,  # noqa: F401  (re-exported for convenience)
    GoogleReauthRequired,
    GoogleServiceError,
    get_google_credentials,
)

# Matches the spreadsheet id inside a docs.google.com/spreadsheets/d/<id> URL.
_SHEET_URL_RE = re.compile(r'/spreadsheets/d/([a-zA-Z0-9_-]+)')

# Default worksheet tabs + column headers written by ``verify_and_setup_sheet``.
DEFAULT_TABS = {
    'Members': ['Name', 'Student ID', 'Email', 'Role', 'Joining Date'],
    'Registrations': ['Event Name', 'Participant Name', 'Phone', 'Status'],
    'Notices': ['Title', 'Date', 'Content', 'Priority'],
}


# ---------------------------------------------------------------------------
# Reference normalization
# ---------------------------------------------------------------------------
def normalize_sheet_ref(ref):
    """Return the spreadsheet key from a URL or a bare reference.

    ``https://docs.google.com/spreadsheets/d/1AbC…/edit`` → ``1AbC…``; a bare
    ID/URL fragment is returned trimmed. Raises ``GoogleServiceError`` when
    empty.
    """
    ref = (ref or '').strip()
    if not ref:
        raise GoogleServiceError('No Google Sheet reference provided.')
    match = _SHEET_URL_RE.search(ref)
    return match.group(1) if match else ref


# ---------------------------------------------------------------------------
# Sheets v4 plumbing (patched out in unit tests)
# ---------------------------------------------------------------------------
def _get_sheets_service(user):
    """Return an authorized Sheets v4 service for ``user``."""
    return build('sheets', 'v4', credentials=get_google_credentials(user))


def _quote_range(title):
    """Quote a sheet title for a range string (titles may contain spaces)."""
    return "'%s'" % title.replace("'", "''")


def _sheet_titles(service, spreadsheet_id):
    """Return the list of worksheet titles in ``spreadsheet_id``."""
    meta = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id, fields='sheets.properties.title',
    ).execute()
    return [sheet['properties']['title'] for sheet in meta.get('sheets') or []]


def _pick_worksheet_title(service, spreadsheet_id, tab_name=None):
    """Resolve the worksheet title to use.

    Returns the tab whose title matches ``tab_name`` (case-insensitive), else
    the first worksheet. Raises ``GoogleServiceError`` when the spreadsheet has
    no sheets at all.
    """
    titles = _sheet_titles(service, spreadsheet_id)
    if not titles:
        raise GoogleServiceError('The spreadsheet has no worksheets.')
    if tab_name:
        for title in titles:
            if title.strip().lower() == tab_name.strip().lower():
                return title
    return titles[0]


def _translate_error(exc):
    """Map a Sheets/transport failure onto the shared error types."""
    if isinstance(exc, RefreshError):
        # A refresh failure always means the stored token is dead → re-consent.
        return GoogleReauthRequired(
            'Your Google session has expired or was revoked — reconnect Google '
            'to continue.'
        )
    if isinstance(exc, HttpError) and exc.resp.status == 403:
        return GoogleServiceError(
            'Google Sheets access denied — share the spreadsheet with your '
            'Google account, or reconnect Google.'
        )
    if isinstance(exc, GoogleServiceError):
        return exc
    return GoogleServiceError('Google Sheets error: %s' % exc)


# ---------------------------------------------------------------------------
# Reads
# ---------------------------------------------------------------------------
def read_rows(user, ref, tab_name=None):
    """Return every row of the selected worksheet, keyed by its header row."""
    try:
        service = _get_sheets_service(user)
        spreadsheet_id = normalize_sheet_ref(ref)
        title = _pick_worksheet_title(service, spreadsheet_id, tab_name)
        response = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='%s!A1:ZZ' % _quote_range(title),
            valueRenderOption='FORMATTED_VALUE',
        ).execute()
        values = response.get('values', [])
        if not values:
            return []
        headers = [str(header).strip() for header in values[0]]
        rows = []
        for raw in values[1:]:
            raw = raw + [''] * (len(headers) - len(raw))
            rows.append(dict(zip(headers, raw)))
        return rows
    except (GoogleAccountNotConnected, GoogleReauthRequired, GoogleServiceError):
        raise
    except Exception as exc:
        raise _translate_error(exc) from exc


def get_members(user, ref, tab_name='Members'):
    """Club member roster rows (headers: Name, Student ID, Email, Role, …)."""
    return read_rows(user, ref, tab_name)


def get_event_registrations(user, ref, tab_name='Registrations'):
    """Event registration rows (headers: Event Name, Participant Name, …)."""
    return read_rows(user, ref, tab_name)


def get_club_notices(user, ref, tab_name='Notices'):
    """Club notice/announcement rows (headers: Title, Date, Content, …)."""
    return read_rows(user, ref, tab_name)


# ---------------------------------------------------------------------------
# Writes
# ---------------------------------------------------------------------------
def append_rows(user, ref, rows, tab_name=None):
    """Append ``rows`` (each a list of cell values) to the worksheet, in order.

    Returns the number of rows written so callers can confirm persistence.
    """
    rows = [list(row) for row in rows if row]
    if not rows:
        return 0
    try:
        service = _get_sheets_service(user)
        spreadsheet_id = normalize_sheet_ref(ref)
        title = _pick_worksheet_title(service, spreadsheet_id, tab_name)
        response = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range='%s!A1' % _quote_range(title),
            valueInputOption='USER_ENTERED',
            body={'values': rows},
        ).execute()
        return response.get('updates', {}).get('updatedRows', len(rows))
    except (GoogleAccountNotConnected, GoogleReauthRequired, GoogleServiceError):
        raise
    except Exception as exc:
        raise _translate_error(exc) from exc


def append_member(user, ref, name, student_id, email='', role='Member', joining_date=''):
    """Append one member row (Name, Student ID, Email, Role, Joining Date)."""
    return append_rows(user, ref, [[name, student_id, email, role, joining_date]], 'Members')


def append_event_registration(user, ref, event_name, participant_name, phone='', status='Registered'):
    """Append one event-registration row (Event Name, Participant Name, Phone, Status)."""
    return append_rows(user, ref, [[event_name, participant_name, phone, status]], 'Registrations')


def append_club_notice(user, ref, title, content='', notice_date='', priority='Normal'):
    """Append one club notice row (Title, Date, Content, Priority)."""
    return append_rows(user, ref, [[title, notice_date, content, priority]], 'Notices')


# ---------------------------------------------------------------------------
# Verify & Connect — create default tabs + column headers
# ---------------------------------------------------------------------------
def verify_and_setup_sheet(user, ref):
    """Open ``ref`` and make sure the default tabs + headers exist.

    Creates the Members / Registrations / Notices tabs when missing and writes
    the default column headers into any tab whose first row is empty. Returns a
    summary dict (spreadsheet title, tabs, and which tabs were created) so the
    Settings UI can confirm the connection.

    Raises ``GoogleServiceError`` (or its auth subtypes) on failure.
    """
    try:
        service = _get_sheets_service(user)
        spreadsheet_id = normalize_sheet_ref(ref)

        meta = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields='properties.title,sheets.properties(sheetId,title)',
        ).execute()
        existing = {
            sheet['properties']['title'].strip().lower(): sheet['properties']['title']
            for sheet in meta.get('sheets') or []
        }
        created = []

        # 1. Create missing tabs.
        missing = [tab for tab in DEFAULT_TABS if tab.lower() not in existing]
        if missing:
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={
                    'requests': [
                        {'addSheet': {'properties': {'title': tab}}} for tab in missing
                    ]
                },
            ).execute()
            for tab in missing:
                existing[tab.lower()] = tab
                created.append(tab)

        # 2. Write default headers into empty tabs.
        for tab, headers in DEFAULT_TABS.items():
            title = existing.get(tab.lower(), tab)
            current = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range='%s!A1:1' % _quote_range(title),
            ).execute().get('values', [])
            if not current or not current[0]:
                service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range='%s!A1:1' % _quote_range(title),
                    valueInputOption='USER_ENTERED',
                    body={'values': [headers]},
                ).execute()

        return {
            'title': meta.get('properties', {}).get('title', ''),
            'tabs': list(DEFAULT_TABS),
            'created': created,
        }
    except (GoogleAccountNotConnected, GoogleReauthRequired, GoogleServiceError):
        raise
    except Exception as exc:
        raise _translate_error(exc) from exc


# ---------------------------------------------------------------------------
# Transaction verification (used by the Club Management dashboard)
# ---------------------------------------------------------------------------
def _column_letter(index):
    """1-based column index → spreadsheet column letter(s) (A, B, …, Z, AA…)."""
    letters = ''
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def verify_club_transaction(sheet_url, trx_id, user, new_status='Verified'):
    """Mark the sheet row matching ``trx_id`` as ``new_status`` in place.

    Locates the header columns for the transaction id and status, finds the
    physical row whose transaction id matches (case-insensitive), and
    overwrites its status cell. Returns the matched row as a header-keyed dict
    so the caller can notify the student it belongs to.

    Raises :class:`GoogleServiceError` when the sheet is missing the required
    columns, no row matches ``trx_id``, or the Google API call itself fails.
    """
    try:
        service = _get_sheets_service(user)
        spreadsheet_id = normalize_sheet_ref(sheet_url)
        title = _pick_worksheet_title(service, spreadsheet_id)
        response = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='%s!A1:ZZ' % _quote_range(title),
            valueRenderOption='FORMATTED_VALUE',
        ).execute()
        values = response.get('values', [])
        if not values:
            raise GoogleServiceError('The sheet is empty — nothing to verify.')
        headers = [str(header).strip() for header in values[0]]
    except (GoogleAccountNotConnected, GoogleReauthRequired, GoogleServiceError):
        raise
    except Exception as exc:
        raise _translate_error(exc) from exc

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

    needle = str(trx_id).strip().lower()
    for row_index, row in enumerate(values[1:], start=2):
        cell = row[trx_col] if trx_col < len(row) else ''
        if str(cell).strip().lower() == needle:
            status_cell = '%s!%s%d' % (
                _quote_range(title), _column_letter(status_col + 1), row_index,
            )
            try:
                service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=status_cell,
                    valueInputOption='USER_ENTERED',
                    body={'values': [[new_status]]},
                ).execute()
            except Exception as exc:
                raise _translate_error(exc) from exc

            row = row + [''] * (len(headers) - len(row))
            row[status_col] = new_status
            return {
                header: row[index] if index < len(row) else ''
                for index, header in enumerate(headers)
            }

    raise GoogleServiceError('No transaction with TrxID %s found in the sheet.' % trx_id)
