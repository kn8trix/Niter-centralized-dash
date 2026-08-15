"""Global news feed for the student & admin dashboards.

Fetches top headlines (or a keyword search) from NewsAPI.org and returns a
normalized article list consumed by ``core.views.student_dashboard``,
``core.views.admin_dashboard`` and the ``/api/news/search/`` endpoint. Each
article carries an optional ``image`` (photo) so the widget can render rich
media cards. Playable video news cards come from a separate YouTube Data API v3
call (:func:`fetch_youtube_videos`), rendered in the widget's dedicated
"Video News" section.

The widget must never take a dashboard down over an external service, so every
failure mode — unset/placeholder API key, network error, timeout, rate limit,
non-200 response — degrades to deterministic sample headlines
(:func:`get_fallback_news_data`). Under the test runner every fetch is skipped
entirely so the suite stays fast and network-free.
"""
import logging
import os
import sys

import requests

logger = logging.getLogger('core.news_service')

NEWS_API_KEY_ENV = 'NEWS_API_KEY'
YOUTUBE_API_KEY_ENV = 'YOUTUBE_API_KEY'
DUMMY_KEY = 'dummy_key'
DEFAULT_CATEGORY = 'technology'
DEFAULT_PAGE_SIZE = 12
YOUTUBE_MAX_RESULTS = 4
TIMEOUT_SECONDS = 5

TOP_HEADLINES_URL = 'https://newsapi.org/v2/top-headlines'
EVERYTHING_URL = 'https://newsapi.org/v2/everything'
YOUTUBE_SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'


def _is_test_run():
    """Mirror ``config.settings._running_tests`` so tests never hit the network.

    ``manage.py test``, the explicit ``TESTING`` env var, or a pytest run
    (``PYTEST_CURRENT_TEST``) all short-circuit straight to the fallback feed.
    """
    return (
        'test' in sys.argv
        or os.environ.get('TESTING', '').lower() in ('1', 'true', 'yes')
        or 'PYTEST_CURRENT_TEST' in os.environ
    )


def _normalize_articles(raw_articles):
    """Map NewsAPI article dicts to the stable shape the templates consume."""
    articles = []
    for article in raw_articles or []:
        if not isinstance(article, dict):
            continue
        title = (article.get('title') or '').strip()
        if not title:
            continue
        source = article.get('source')
        articles.append({
            'title': title,
            'description': (article.get('description') or '').strip(),
            'url': article.get('url') or '',
            'image': article.get('urlToImage') or '',
            'video_url': '',
            'source': source.get('name', '') if isinstance(source, dict) else '',
            'published_at': article.get('publishedAt') or '',
        })
    return articles


def fetch_youtube_videos(query=None, max_results=YOUTUBE_MAX_RESULTS):
    """Query the YouTube Data API v3 for playable video news cards.

    Searches ``{query} news`` (or ``{DEFAULT_CATEGORY} news`` without a query)
    with ``type=video`` and returns the **raw API items** (``id.videoId`` /
    ``snippet.title`` / ``snippet.channelTitle`` / thumbnails) so the widget
    template can build ``https://www.youtube.com/embed/<videoId>`` players
    directly. Only runs when a real ``YOUTUBE_API_KEY`` is configured; without
    one (or on any network/API error) it returns ``[]`` so the news feed is
    never held hostage by a second external service.
    """
    if _is_test_run():
        return []
    api_key = os.getenv(YOUTUBE_API_KEY_ENV, '').strip()
    if not api_key or api_key == DUMMY_KEY:
        return []
    q = '%s news' % ((query or '').strip() or DEFAULT_CATEGORY)
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
            'YouTube API returned status %s — skipping video news.',
            response.status_code,
        )
    except Exception as exc:  # network errors, timeouts, bad JSON — degrade gracefully
        logger.warning('YouTube API fetch error: %s', exc)
    return []


def get_fallback_news_data(query=None):
    """Deterministic sample headlines used when the live API is unavailable.

    Returns the same article shape as :func:`fetch_global_news` (title /
    description / url / image / source / published_at) so the dashboards
    render identically either way. ``query`` flavors the headlines so a search
    still looks relevant even in degraded mode.
    """
    if query:
        label = query.strip().title()
        articles = [
            {
                'title': f'{label}: what to know this week',
                'description': (
                    f'A quick briefing on the latest {label} developments, '
                    'pulled together from the global wires.'
                ),
                'url': 'https://news.google.com/search?q=' + query.strip(),
                'image': '',
                'video_url': '',
                'source': 'Sample Wire',
                'published_at': '',
            },
            {
                'title': f'Five {label} trends shaping the next quarter',
                'description': (
                    f'Analysts highlight the {label} stories most likely to '
                    'move the conversation in the coming months.'
                ),
                'url': 'https://news.google.com/search?q=' + query.strip(),
                'image': '',
                'video_url': '',
                'source': 'Sample Wire',
                'published_at': '',
            },
            {
                'title': f'Why experts are watching {label} right now',
                'description': (
                    'A closer look at the forces behind the headlines and '
                    'what they mean for everyday readers.'
                ),
                'url': 'https://news.google.com/search?q=' + query.strip(),
                'image': '',
                'video_url': '',
                'source': 'Sample Wire',
                'published_at': '',
            },
        ]
    else:
        articles = [
            {
                'title': 'Researchers unveil a new approach to sustainable campus energy',
                'description': (
                    'A pilot project on university rooftops pairs solar arrays '
                    'with smart storage to cut peak-hour grid demand.'
                ),
                'url': 'https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB',
                'image': '',
                'video_url': '',
                'source': 'Sample Wire',
                'published_at': '',
            },
            {
                'title': 'AI tutors show promise in early university trials',
                'description': (
                    'Pilot courses report faster homework turnaround and more '
                    'personalized feedback, while faculty weigh the trade-offs.'
                ),
                'url': 'https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB',
                'image': '',
                'video_url': '',
                'source': 'Sample Wire',
                'published_at': '',
            },
            {
                'title': 'Campus libraries go hybrid with 24/7 digital study rooms',
                'description': (
                    'New booking systems let students reserve quiet study pods '
                    'round the clock, online or in person.'
                ),
                'url': 'https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB',
                'image': '',
                'video_url': '',
                'source': 'Sample Wire',
                'published_at': '',
            },
            {
                'title': 'Student-built weather station network expands to 40 schools',
                'description': (
                    'Low-cost sensors stream local conditions to a shared '
                    'dashboard used by science classes across the region.'
                ),
                'url': 'https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB',
                'image': '',
                'video_url': '',
                'source': 'Sample Wire',
                'published_at': '',
            },
            {
                'title': 'Open-source tools gain ground in university software courses',
                'description': (
                    'Instructors say real-world open-source contributions are '
                    'becoming a staple of the modern CS curriculum.'
                ),
                'url': 'https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB',
                'image': '',
                'video_url': '',
                'source': 'Sample Wire',
                'published_at': '',
            },
            {
                'title': 'New scholarship fund backs student climate research',
                'description': (
                    'The grant supports undergraduate projects on renewable '
                    'energy, conservation, and climate resilience.'
                ),
                'url': 'https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB',
                'image': '',
                'video_url': '',
                'source': 'Sample Wire',
                'published_at': '',
            },
        ]
    return articles


def fetch_global_news(query=None, category=DEFAULT_CATEGORY, page_size=DEFAULT_PAGE_SIZE):
    """Fetch top headlines or keyword search results from NewsAPI.org.

    ``query`` uses the ``/everything`` endpoint (keyword search); otherwise the
    ``/top-headlines`` endpoint is used with ``category``. Always returns a
    list — real articles when the API cooperates, deterministic samples
    otherwise (see module docstring for the fallback policy). Video news cards
    are fetched separately via :func:`fetch_youtube_videos`.
    """
    if _is_test_run():
        return get_fallback_news_data(query)

    api_key = os.getenv(NEWS_API_KEY_ENV, DUMMY_KEY)
    if not api_key or api_key == DUMMY_KEY:
        return get_fallback_news_data(query)

    if query:
        url = EVERYTHING_URL
        params = {
            'apiKey': api_key,
            'q': query,
            'language': 'en',
            'pageSize': page_size,
        }
    else:
        url = TOP_HEADLINES_URL
        params = {
            'apiKey': api_key,
            'language': 'en',
            'pageSize': page_size,
            'category': category,
        }

    try:
        response = requests.get(url, params=params, timeout=TIMEOUT_SECONDS)
        if response.status_code == 200:
            return _normalize_articles(response.json().get('articles', []))
        logger.warning(
            'News API returned status %s for %s — using fallback feed.',
            response.status_code,
            url,
        )
    except Exception as exc:  # network errors, timeouts, bad JSON — degrade gracefully
        logger.warning('News API fetch error: %s', exc)

    return get_fallback_news_data(query)
