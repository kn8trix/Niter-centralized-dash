"""Attendance QR-dispatch + report email service.

Server-side helpers for the Admin Attendance dashboard:

* ``attendance_qr_png``        — renders a class-session QR payload to a PNG
  (the ``qrcode`` library with its Pillow image backend).
* ``attendance_report``        — builds the per-session attendance summary
  (student list, IDs, present/absent, check-in timestamps) plus a styled
  HTML table and a CSV attachment payload.
* ``email_qr_to_teacher``      — sends the class QR code + session details
  (course, token, expiry) to the assigned course teacher.
* ``email_report_to_teacher``  — sends the styled HTML report + CSV to the
  assigned course teacher.

Both senders use the configured Django email backend (Gmail SMTP in
production, console backend in local dev) and raise the underlying
``SMTPException`` on failure so the caller can answer 502 / fall back.
"""

import csv
import io

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.utils import timezone

from core.models import AttendanceRecord

try:
    import qrcode
    from qrcode.image.pil import PilImage

    QR_AVAILABLE = True
except ImportError:  # pragma: no cover - qrcode[pil] is pinned in requirements
    QR_AVAILABLE = False


def _session_course_label(session):
    """Short human label for the course a session belongs to, e.g. 'CS101'."""
    return getattr(session, 'course_code', '') or '—'


def _fmt_slot(timestamp):
    """Locale-safe short timestamp, e.g. '12 Aug, 10:05 AM'."""
    if not timestamp:
        return '—'
    return timestamp.strftime('%d %b, %I:%M %p')


def attendance_qr_png(session, box_size=8, border=2):
    """Render the session QR payload (``ATT|<token>``) to PNG bytes.

    ``box_size`` / ``border`` follow the qrcode library defaults scaled for
    classroom projection — a 200×200px image at the default box size.
    """
    payload = 'ATT|' + session.session_token
    if not QR_AVAILABLE:  # pragma: no cover - library pinned in requirements
        return None
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    image = qr.make_image(image_factory=PilImage, fill_color='black', back_color='white')
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return buffer.getvalue()


def attendance_report(session):
    """Build the per-session attendance summary for ``session``.

    Returns a dict with the ``rows`` (one per enrolled-scope student:
    name / student id / status / check-in timestamp — students with no
    record count as Absent), plus ``html`` (a styled, inline-CSS summary
    table ready for an email body) and ``csv_bytes`` / ``csv_name`` for the
    CSV attachment. ``present`` / ``absent`` totals are included too.
    """
    # Roster = every student who has attended ANY session of the same course
    # (the AttendanceSession has no enrolled-student FK, so the course's
    # student pool is derived from its attendance history). Students without a
    # record for THIS session are reported Absent.
    present_records = list(
        session.records.select_related('student__student_profile').order_by('timestamp')
    )

    roster = []
    roster_ids = set()
    for record in (
        AttendanceRecord.objects.filter(session__course_code__iexact=session.course_code)
        .select_related('student__student_profile')
        .order_by('timestamp')
    ):
        if record.student_id in roster_ids:
            continue
        roster_ids.add(record.student_id)
        profile = getattr(record.student, 'student_profile', None)
        roster.append({
            'pk': record.student_id,
            'student_name': record.student.get_full_name() or record.student.username,
            'student_id': (profile.student_id if profile else '') or record.student.username,
        })
    roster.sort(key=lambda row: row['student_name'].lower())

    present_by_pk = {record.student_id: record for record in present_records}
    rows = []
    for entry in roster:
        matched = present_by_pk.get(entry['pk'])
        if matched is not None:
            rows.append({
                'student_name': entry['student_name'],
                'student_id': entry['student_id'],
                'status': matched.get_status_display(),
                'timestamp': matched.timestamp,
            })
        else:
            rows.append({
                'student_name': entry['student_name'],
                'student_id': entry['student_id'],
                'status': 'Absent',
                'timestamp': None,
            })

    present = sum(1 for row in rows if row['status'] == 'Present')
    total = len(rows)

    for row in rows:
        row['timestamp_label'] = _fmt_slot(row['timestamp'])

    html = _report_html(session, rows, present, total)
    csv_bytes = _report_csv(session, rows)
    return {
        'rows': rows,
        'html': html,
        'csv_bytes': csv_bytes,
        'csv_name': 'attendance-%s-%s.csv' % (
            session.course_code.lower(), session.session_token.lower(),
        ),
        'present': present,
        'absent': total - present,
        'total': total,
    }


def _report_html(session, rows, present, total):
    """Styled inline-CSS HTML summary table for the email body."""
    rows_html = ''.join(
        '<tr>'
        '<td style="padding:8px 12px;border-bottom:1px solid #eee;">%s</td>'
        '<td style="padding:8px 12px;border-bottom:1px solid #eee;color:#666;">%s</td>'
        '<td style="padding:8px 12px;border-bottom:1px solid #eee;">'
        '<span style="background:#e8f5e9;color:#2e7d32;padding:2px 8px;'
        'border-radius:10px;font-size:12px;">%s</span></td>'
        '<td style="padding:8px 12px;border-bottom:1px solid #eee;color:#666;">%s</td>'
        '</tr>'
        % (
            escape_html(row['student_name']),
            escape_html(row['student_id']),
            escape_html(row['status']),
            escape_html(row['timestamp_label']),
        )
        for row in rows
    )
    if not rows:
        rows_html = (
            '<tr><td colspan="4" style="padding:12px;text-align:center;color:#999;">'
            'No students have checked in yet.</td></tr>'
        )
    return (
        '<div style="font-family:Inter,Arial,sans-serif;max-width:640px;margin:0 auto;">'
        '<h2 style="margin:0 0 4px;color:#2B2927;">Attendance Summary</h2>'
        '<p style="margin:0 0 16px;color:#666;">%s — Session %s</p>'
        '<p style="margin:0 0 12px;color:#444;">'
        'Present: <strong>%d</strong> · Absent: <strong>%d</strong></p>'
        '<table style="width:100%%;border-collapse:collapse;background:#fff;'
        'border:1px solid #e5e0d8;border-radius:8px;overflow:hidden;">'
        '<thead><tr style="background:#f7f4ee;text-align:left;">'
        '<th style="padding:8px 12px;">Student</th>'
        '<th style="padding:8px 12px;">Student ID</th>'
        '<th style="padding:8px 12px;">Status</th>'
        '<th style="padding:8px 12px;">Check-in</th>'
        '</tr></thead><tbody>%s</tbody></table>'
        '<p style="margin:16px 0 0;color:#999;font-size:12px;">'
        'Generated by Niter Hub — Attendance System · %s</p>'
        '</div>'
    ) % (
        escape_html(_session_course_label(session)),
        escape_html(session.session_token),
        present,
        total - present,
        rows_html,
        timezone.now().strftime('%d %b %Y, %I:%M %p'),
    )


def _report_csv(session, rows):
    """CSV payload for the report attachment (student list, ID, status, time)."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(['Course', 'Session', 'Token', 'Student Name', 'Student ID', 'Status', 'Check-in Time'])
    for row in rows:
        writer.writerow([
            session.course_code,
            session.session_token,
            session.session_token,
            row['student_name'],
            row['student_id'],
            row['status'],
            row['timestamp_label'],
        ])
    return buffer.getvalue().encode('utf-8')


def email_qr_to_teacher(session, teacher):
    """Email the class QR PNG + session details to the assigned teacher.

    Returns the number of recipients. Raises on SMTP failure so the caller
    can surface a friendly error (or log-and-continue for auto-dispatch).
    """
    png = attendance_qr_png(session)
    subject = 'Class QR Code — %s (Session %s)' % (
        _session_course_label(session), session.session_token,
    )
    body = (
        'Dear %s,\n\n'
        'Please find attached the QR code for your %s class session.\n\n'
        '  Session token : %s\n'
        '  Expires at    : %s\n'
        '  Scan payload  : ATT|%s\n\n'
        'Project the attached QR image in class so students can mark '
        'themselves Present by scanning it.\n\n'
        '— Niter Hub Attendance System'
    ) % (
        teacher.name,
        _session_course_label(session),
        session.session_token,
        _fmt_slot(session.expires_at),
        session.session_token,
    )
    message = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[teacher.email],
    )
    if png is not None:
        message.attach(
            'class-qr-%s.png' % session.session_token.lower(), png, 'image/png',
        )
    return message.send(fail_silently=False)


def email_report_to_teacher(session, teacher, report=None):
    """Email the styled HTML attendance summary + CSV to the course teacher.

    ``report`` may be prebuilt (avoids rebuilding when the caller already has
    it); it is rebuilt from ``session`` when omitted. Returns the number of
    recipients; raises on SMTP failure.
    """
    report = report or attendance_report(session)
    subject = 'Attendance Report — %s (Session %s)' % (
        _session_course_label(session), session.session_token,
    )
    text_body = (
        'Dear %s,\n\n'
        'Here is the attendance summary for your %s class session %s.\n'
        'Present: %d. See the attached CSV for the full list.\n\n'
        '— Niter Hub Attendance System'
    ) % (
        teacher.name,
        _session_course_label(session),
        session.session_token,
        report['present'],
    )
    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[teacher.email],
    )
    message.attach_alternative(report['html'], 'text/html')
    message.attach(report['csv_name'], report['csv_bytes'], 'text/csv')
    return message.send(fail_silently=False)


def escape_html(value):
    """Minimal HTML escaping for report cells (safer than raw %s in tables)."""
    return (
        str(value)
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
    )
