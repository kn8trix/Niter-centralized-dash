"""Study Corner backend — YouTube lecture videos + AI Study Assistant.

The Study Corner page (``/study-corner/``) combines the Academic Notes drive
with a YouTube lecture-video search module and an AI chat tutor. This module
owns the two external integrations:

* :func:`search_lecture_videos` — YouTube Data API v3 keyword search for
  lectures/tutorials. Returns the **raw API items** (``id.videoId`` /
  ``snippet.title`` / ``snippet.channelTitle`` / thumbnails) so the template
  can build ``https://www.youtube.com/embed/<videoId>`` players directly.
* :func:`offline_study_response` — deterministic Study Assistant reply used
  when no ``OPENROUTER_API_KEY`` is configured (the live chat goes through
  ``services.openrouter.call_openrouter`` with :data:`STUDY_SYSTEM_PROMPT`).

Every external call degrades gracefully (``[]`` / canned reply) so the page
never breaks over a third-party service; under the test runner nothing hits
the network.
"""
import logging
import os
import sys

import requests

logger = logging.getLogger('core.study_service')

YOUTUBE_API_KEY_ENV = 'YOUTUBE_API_KEY'
DUMMY_KEY = 'dummy_key'
YOUTUBE_SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'
# Used when the module is rendered with no explicit search query.
STUDY_DEFAULT_QUERY = 'university lecture'
STUDY_MAX_RESULTS = 6
TIMEOUT_SECONDS = 5

# System prompt for the Study Assistant chat (OpenRouter-backed).
STUDY_SYSTEM_PROMPT = (
    'You are the NITER Study Assistant — a friendly, concise tutor for '
    'engineering and textile university students. Help with course concepts, '
    'homework (explain the approach rather than just handing over the answer), '
    'exam revision plans, and effective study techniques. Keep answers clear '
    'and structured with Markdown: short headings, bullet points, and worked '
    'examples where they help. Encourage understanding over memorization.'
)


def _is_test_run():
    """Mirror ``config.settings._running_tests`` so tests never hit the network.

    ``manage.py test``, the explicit ``TESTING`` env var, or a pytest run
    (``PYTEST_CURRENT_TEST``) all short-circuit to the deterministic fallbacks.
    """
    return (
        'test' in sys.argv
        or os.environ.get('TESTING', '').lower() in ('1', 'true', 'yes')
        or 'PYTEST_CURRENT_TEST' in os.environ
    )


def search_lecture_videos(query=None, max_results=STUDY_MAX_RESULTS):
    """Query the YouTube Data API v3 for lecture/tutorial videos.

    Searches ``{query} lecture tutorial`` (or :data:`STUDY_DEFAULT_QUERY` when
    no query is given) with ``type=video`` and returns the raw API items
    filtered to real videos. Only runs when a real ``YOUTUBE_API_KEY`` is
    configured; without one (or on any network/API error) it returns ``[]`` so
    the Study Corner page is never held hostage by a second external service.
    """
    if _is_test_run():
        return []
    api_key = os.getenv(YOUTUBE_API_KEY_ENV, '').strip()
    if not api_key or api_key == DUMMY_KEY:
        return []
    query = (query or '').strip()
    q = '%s lecture tutorial' % query if query else STUDY_DEFAULT_QUERY
    try:
        response = requests.get(YOUTUBE_SEARCH_URL, params={
            'part': 'snippet',
            'type': 'video',
            'q': q,
            'maxResults': max_results,
            'key': api_key,
        }, timeout=TIMEOUT_SECONDS)
        if response.status_code == 200:
            items = response.json().get('items') or []
            # Keep only real videos (skip playlists/channels/malformed rows).
            return [item for item in items
                    if isinstance(item, dict) and (item.get('id') or {}).get('videoId')][:max_results]
        logger.warning(
            'YouTube API returned status %s — no lecture videos.',
            response.status_code,
        )
    except Exception as exc:  # network errors, timeouts, bad JSON — degrade gracefully
        logger.warning('YouTube lecture search error: %s', exc)
    return []


def offline_study_response(message):
    """Deterministic Study Assistant reply when OpenRouter isn't configured.

    Returns a short, useful study framework keyed to the user's question so
    the chat widget stays usable with zero configuration.
    """
    topic = ((message or '').strip()[:120]) or 'your question'
    return (
        "I'm your Study Assistant. The AI provider isn't configured yet, so "
        "here's a quick study framework for **%s** instead:\n\n"
        "1. **Chunk it** — break the topic into small, testable concepts and "
        "master one at a time.\n"
        "2. **Active recall** — close your notes and explain each idea out "
        "loud; quiz yourself daily.\n"
        "3. **Spaced practice** — revisit the material tomorrow, then in 3 "
        "days, then weekly.\n"
        "4. **Teach it** — if you can explain it simply, you know it.\n\n"
        "Once OPENROUTER_API_KEY is configured, I'll answer this with full "
        "worked explanations." % topic
    )
