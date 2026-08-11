"""Huey background tasks — work offloaded from the request/response cycle.

Tasks are executed by the Huey consumer (``python manage.py run_huey`` on the
Render worker service). In dev/tests HUEY runs in ``immediate`` mode, so the
same task executes synchronously in-process and the API keeps answering with
inline results.
"""

import logging

from django.utils import timezone
from huey.contrib.djhuey import db_task

from .consumers import notify_user
from .models import NoteAnalysis, Notice, Notification, User
from .notes_analysis import count_sentences, extract_keywords, extract_summary

logger = logging.getLogger('core.tasks')


def _push_notification(notification):
    """Push a freshly-created Notification over the user's WebSocket group.

    Mirrors ``core.views._broadcast_notification`` so background-created
    notifications reach the same live bell channel.
    """
    notify_user(notification.user_id, {
        'id': notification.pk,
        'title': notification.title,
        'message': notification.message,
        'category': notification.category,
        'is_read': notification.is_read,
        'created_at': notification.created_at.isoformat(),
    })


@db_task()
def broadcast_notice(notice_id, bell_category):
    """Fan out a published ``Notice`` to every active user (+ live push).

    Off the request path so publishing a notice never stalls the staff
    action on a large student body. Idempotent by nature: each publish
    creates one notification per active user. Returns the created count
    (useful in immediate mode).
    """
    try:
        notice = Notice.objects.get(pk=notice_id)
    except Notice.DoesNotExist:
        logger.warning('broadcast_notice: notice %s not found', notice_id)
        return 0

    notified = 0
    for student in User.objects.filter(is_active=True):
        notification = Notification.objects.create(
            user=student,
            title='New notice: %s' % notice.title,
            message='%s — %s' % (notice.get_category_display(), notice.title),
            category=bell_category,
        )
        _push_notification(notification)
        notified += 1
    return notified


@db_task()
def analyze_note_content(analysis_id):
    """Compute summary + keywords for a ``NoteAnalysis`` row in the background.

    ``db_task`` opens a dedicated DB connection in the worker and closes it
    afterwards, so long-running consumers never leak connections.
    """
    try:
        analysis = NoteAnalysis.objects.get(pk=analysis_id)
    except NoteAnalysis.DoesNotExist:
        logger.warning('analyze_note_content: analysis %s not found', analysis_id)
        return

    if analysis.status == 'done':
        return  # idempotent — a retried task must not recompute

    analysis.status = 'processing'
    analysis.save(update_fields=['status'])

    try:
        analysis.summary = extract_summary(analysis.content)
        analysis.keywords = extract_keywords(analysis.content)
        analysis.sentence_count = count_sentences(analysis.content)
        analysis.status = 'done'
    except Exception:
        logger.exception('analyze_note_content failed for analysis %s', analysis_id)
        analysis.status = 'failed'
        analysis.error_message = 'Analysis failed — please try again.'
    analysis.completed_at = timezone.now()
    analysis.save()
