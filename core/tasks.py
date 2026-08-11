"""Huey background tasks — work offloaded from the request/response cycle.

Tasks are executed by the Huey consumer (``python manage.py run_huey`` on the
Render worker service). In dev/tests HUEY runs in ``immediate`` mode, so the
same task executes synchronously in-process and the API keeps answering with
inline results.
"""

import logging

from django.utils import timezone
from huey.contrib.djhuey import db_task

from .models import NoteAnalysis
from .notes_analysis import count_sentences, extract_keywords, extract_summary

logger = logging.getLogger('core.tasks')


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
