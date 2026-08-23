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
from .models import (
    CourseMaterial,
    EmergencyAlert,
    NoteAnalysis,
    Notice,
    Notification,
    User,
    VectorDocument,
)
from .notes_analysis import count_sentences, extract_keywords, extract_summary
from services import vector_store
from services.parser import extract_document_text

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
def broadcast_emergency_alert(alert_id):
    """Fan out an ``EmergencyAlert`` to every active user's notification bell.

    Mirrors ``broadcast_notice``: one ``Notification`` row per active user so
    the topbar bell keeps the alert after the siren banner is dismissed, and
    each row is pushed over the user's WebSocket group in real time. Runs off
    the admin's trigger request path (immediate mode in dev/tests). Returns
    the number of users notified.
    """
    try:
        alert = EmergencyAlert.objects.get(pk=alert_id)
    except EmergencyAlert.DoesNotExist:
        logger.warning('broadcast_emergency_alert: alert %s not found', alert_id)
        return 0

    notified = 0
    for student in User.objects.filter(is_active=True):
        notification = Notification.objects.create(
            user=student,
            title='\U0001F6A8 %s' % alert.title,
            message=alert.message,
            category='urgent',
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


# --- Vector-store (RAG) indexing --------------------------------------------
# Restricted to Study Corner + Research AI. Each task extracts/receives text,
# then chunks → embeds → upserts into ChromaDB via ``services.vector_store`` and
# records the outcome on a ``VectorDocument`` tracking row. In dev/tests HUEY is
# in ``immediate`` mode, so these run inline right after upload; in production
# the Huey consumer runs them off the request path. Every failure is caught so
# indexing never breaks the upload / chat flow.

def _finalize_vector_document(doc, chunk_count):
    """Stamp a ``VectorDocument`` row from an indexing result."""
    if chunk_count > 0:
        doc.status = VectorDocument.STATUS_INDEXED
        doc.chunk_count = chunk_count
        doc.error_message = ''
    else:
        doc.status = VectorDocument.STATUS_FAILED
        doc.chunk_count = 0
        doc.error_message = 'No extractable text (unsupported format or empty file).'
    doc.indexed_at = timezone.now()
    doc.save()


@db_task()
def index_course_material(material_id):
    """Index a Study Corner ``CourseMaterial`` upload into the vector store.

    Opens the stored file, extracts its plain text (PDF/DOCX), and indexes it
    into the shared ``study_corner`` collection (no owner — Study Corner is a
    shared catalog). Returns the number of chunks indexed.
    """
    try:
        material = CourseMaterial.objects.select_related('course').get(pk=material_id)
    except CourseMaterial.DoesNotExist:
        logger.warning('index_course_material: material %s not found', material_id)
        return 0
    if not material.file:
        return 0

    doc, _created = VectorDocument.objects.update_or_create(
        module=VectorDocument.MODULE_STUDY_CORNER,
        source_type='course_material',
        source_id=str(material.pk),
        defaults={
            'title': material.title,
            'owner': None,
            'status': VectorDocument.STATUS_PENDING,
        },
    )
    try:
        material.file.open('rb')
        try:
            text = extract_document_text(material.file)
        finally:
            material.file.close()
        chunk_count = vector_store.index(
            vector_store.STUDY_CORNER,
            material.pk,
            text or '',
            metadata={
                'title': material.title,
                'course': material.course.code,
                'source_type': 'course_material',
            },
        )
        _finalize_vector_document(doc, chunk_count)
        return chunk_count
    except Exception:
        logger.exception('index_course_material failed for %s', material_id)
        doc.status = VectorDocument.STATUS_FAILED
        doc.error_message = 'Indexing failed — see server logs.'
        doc.indexed_at = timezone.now()
        doc.save()
        return 0


@db_task()
def index_research_document(owner_id, source_id, text, title=''):
    """Index an already-extracted Research AI reference document.

    Research AI extracts the uploaded file's text in the request (it is not
    persisted as a model), so the plain ``text`` is passed straight in and
    indexed into the ``research_ai`` collection scoped to ``owner_id`` — each
    user only ever retrieves their own uploaded references.
    """
    if not (text or '').strip():
        return 0

    doc, _created = VectorDocument.objects.update_or_create(
        module=VectorDocument.MODULE_RESEARCH_AI,
        source_type='research_upload',
        source_id=str(source_id),
        defaults={
            'title': title or '',
            'owner_id': owner_id,
            'status': VectorDocument.STATUS_PENDING,
        },
    )
    try:
        chunk_count = vector_store.index(
            vector_store.RESEARCH_AI,
            source_id,
            text,
            metadata={'title': title or '', 'source_type': 'research_upload'},
            owner=owner_id,
        )
        _finalize_vector_document(doc, chunk_count)
        return chunk_count
    except Exception:
        logger.exception('index_research_document failed for %s', source_id)
        doc.status = VectorDocument.STATUS_FAILED
        doc.error_message = 'Indexing failed — see server logs.'
        doc.indexed_at = timezone.now()
        doc.save()
        return 0
