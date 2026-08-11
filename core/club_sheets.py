"""Club Google Sheets data layer — members, event registrations, club notices.

High-level read/write helpers built on the shared Google service layer
(``core.google_service``). Every call rebuilds the calling user's stored OAuth
credentials (``GoogleUserToken``) and talks to the connected club spreadsheet
through ``gspread``.

- References accept either a full ``docs.google.com/spreadsheets/d/…`` URL or a
  bare Sheet ID — both are normalized transparently.
- Datasets map to worksheet tabs by name (Members / Registrations / Notices);
  when the named tab is missing, the first worksheet is used, so a single-tab
  sheet keeps working unchanged.

All Google/API failures surface as :class:`core.google_service.GoogleServiceError`
(with the :class:`GoogleReauthRequired` / :class:`GoogleAccountNotConnected`
subtypes), so views can answer 401 (re-connect Google) or 500 accordingly.
"""

import re

import gspread
from google.auth.exceptions import RefreshError

from .google_service import (
    GoogleAccountNotConnected,  # noqa: F401  (re-exported for convenience)
    GoogleReauthRequired,
    GoogleServiceError,
    get_google_credentials,
)

# Matches the spreadsheet id inside a docs.google.com/spreadsheets/d/<id> URL.
_SHEET_URL_RE = re.compile(r'/spreadsheets/d/([a-zA-Z0-9_-]+)')


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
# Low-level gspread plumbing (patched out in unit tests)
# ---------------------------------------------------------------------------
def _authorize_client(user):
    """Return an authorized gspread client for ``user`` (rebuilds credentials)."""
    return gspread.authorize(get_google_credentials(user))


def _open_spreadsheet(user, ref):
    """Open the club spreadsheet by key (URLs are normalized first)."""
    key = normalize_sheet_ref(ref)
    return _authorize_client(user).open_by_key(key)


def _pick_worksheet(spreadsheet, tab_name=None):
    """Select a worksheet by tab name (case-insensitive), else the first one."""
    if tab_name:
        try:
            return spreadsheet.worksheet(tab_name)
        except gspread.exceptions.WorksheetNotFound:
            pass
    first = getattr(spreadsheet, 'sheet1', None)
    return first if first is not None else spreadsheet.get_worksheet(0)


def _translate_error(exc):
    """Map a Google/transport failure onto the shared error types."""
    if isinstance(exc, (RefreshError, gspread.exceptions.APIError)) and 'expired' in str(exc).lower():
        return GoogleReauthRequired(
            'Your Google session has expired — reconnect Google to continue.'
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
        worksheet = _pick_worksheet(_open_spreadsheet(user, ref), tab_name)
        return worksheet.get_all_records()
    except (GoogleAccountNotConnected, GoogleReauthRequired, GoogleServiceError):
        raise
    except Exception as exc:
        raise _translate_error(exc) from exc


def get_members(user, ref, tab_name='Members'):
    """Club member roster rows (headers: Name, Student ID, Club, Role, …)."""
    return read_rows(user, ref, tab_name)


def get_event_registrations(user, ref, tab_name='Registrations'):
    """Event registration rows (headers: Name, Student ID, Event, TrxID, …)."""
    return read_rows(user, ref, tab_name)


def get_club_notices(user, ref, tab_name='Notices'):
    """Club notice/announcement rows (headers: Title, Body, Date, …)."""
    return read_rows(user, ref, tab_name)


# ---------------------------------------------------------------------------
# Writes
# ---------------------------------------------------------------------------
def append_rows(user, ref, rows, tab_name=None):
    """Append ``rows`` (each a list of cell values) to the worksheet, in order.

    Returns the number of rows written so callers can confirm persistence.
    """
    rows = [list(r) for r in rows if r]
    if not rows:
        return 0
    try:
        worksheet = _pick_worksheet(_open_spreadsheet(user, ref), tab_name)
        for row in rows:
            worksheet.append_row(row)
        return len(rows)
    except (GoogleAccountNotConnected, GoogleReauthRequired, GoogleServiceError):
        raise
    except Exception as exc:
        raise _translate_error(exc) from exc


def append_member(user, ref, name, student_id, club='', role='Member'):
    """Append one member row (Name, Student ID, Club, Role)."""
    return append_rows(user, ref, [[name, student_id, club, role]], 'Members')


def append_event_registration(user, ref, name, student_id, event, trx_id='', status='Registered'):
    """Append one event-registration row (Name, Student ID, Event, TrxID, Status)."""
    return append_rows(user, ref, [[name, student_id, event, trx_id, status]], 'Registrations')


def append_club_notice(user, ref, title, body='', notice_date=''):
    """Append one club notice row (Title, Body, Date)."""
    return append_rows(user, ref, [[title, body, notice_date]], 'Notices')
