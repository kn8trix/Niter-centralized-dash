"""Global news feed for the student & admin dashboards.

Fetches top headlines (or a keyword search) from NewsAPI.org, enriches keyword
searches with YouTube video cards (when ``YOUTUBE_API_KEY`` is configured), and
returns a normalized article list consumed by ``core.views.student_dashboard``,
``core.views.admin_dashboard`` and the ``/api/news/search/`` endpoint. Each
article carries an optional ``image`` (photo) and/or ``video_url`` (embedded
video) so the widget can render rich media cards.

The widget must never take a dashboard down over an external service, so every
failure mode — unset/placeholder API key, network error, timeout, rate limit,
non-200 response — degrades to deterministic sample headlines
(:func:`get_fallback_news_data`). Under the test runner the fetch is skipped
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
TIMEOUT_SECONDS = 5

TOP_HEADLINES_URL = 'https://newsapi.org/v2/top-headlines'
EVERYTHING_URL = 'https://newsapi.org/v2/everything'
YOUTUBE_SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'
YOUTUBE_WATCH_URL = 'https://www.youtube.com/watch?v=%s'
YOUTUBE_EMBED_URL = 'https://www.youtube.com/embed/%s'


def _interleave(articles, videos):
    """Merge two lists alternately (articles first), preserving both orders.

    Used to sprinkle YouTube video cards through a keyword search feed instead
    of dumping them all at the end.
    """
    merged = []
    ai = vi = 0
    while ai < len(articles) or vi < len(videos):
        if ai < len(articles):
            merged.append(articles[ai])
            ai += 1
        if vi < len(videos):
            merged.append(videos[vi])
            vi += 1
    return merged


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


def _normalize_videos(raw_items):
    """Map YouTube Data API v3 search items to the shared article shape.

    Video cards carry ``video_url`` (an embeddable watch URL) and no ``image``
    — the template renders an iframe instead of a photo. ``url`` stays the
    canonical watch page so the card still opens on YouTube.
    """
    videos = []
    for item in raw_items or []:
        if not isinstance(item, dict):
            continue
        snippet = item.get('snippet') or {}
        video_id = ((item.get('id') or {}).get('videoId') or '').strip()
        title = (snippet.get('title') or '').strip()
        if not video_id or not title:
            continue
        videos.append({
            'title': title,
            'description': (snippet.get('description') or '').strip(),
            'url': YOUTUBE_WATCH_URL % video_id,
            'image': '',
            'video_url': YOUTUBE_EMBED_URL % video_id,
            'source': (snippet.get('channelTitle') or 'Video').strip(),
            'published_at': snippet.get('publishedAt') or '',
        })
    return videos


def _fetch_youtube_videos(query, page_size):
    """YouTube Data API v3 keyword search → video cards (or [] when unused).

    Only runs when a real ``YOUTUBE_API_KEY`` is configured; without one (or on
    any network/API error) it returns ``[]`` so the news feed is never held
    hostage by a second external service.
    """
    api_key = os.getenv(YOUTUBE_API_KEY_ENV, '').strip()
    if not api_key or api_key == DUMMY_KEY:
        return []
    try:
        response = requests.get(YOUTUBE_SEARCH_URL, params={
            'part': 'snippet',
            'type': 'video',
            'q': query,
            'maxResults': page_size,
            'key': api_key,
        }, timeout=TIMEOUT_SECONDS)
        if response.status_code == 200:
            return _normalize_videos(response.json().get('items', []))
        logger.warning(
            'YouTube API returned status %s — skipping video cards.',
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

    ``query`` uses the ``/everything`` endpoint (keyword search) and, when a
    ``YOUTUBE_API_KEY`` is configured, enriches the feed with video cards from
    the YouTube Data API v3 (interleaved through the result list). Otherwise
    the ``/top-headlines`` endpoint is used with ``category``. Always returns a
    list — real articles when the APIs cooperate, deterministic samples
    otherwise (see module docstring for the fallback policy).
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

    articles = None
    try:
        response = requests.get(url, params=params, timeout=TIMEOUT_SECONDS)
        if response.status_code == 200:
            articles = _normalize_articles(response.json().get('articles', []))
        else:
            logger.warning(
                'News API returned status %s for %s — using fallback feed.',
                response.status_code,
                url,
            )
    except Exception as exc:  # network errors, timeouts, bad JSON — degrade gracefully
        logger.warning('News API fetch error: %s', exc)

    if articles is None:
        return get_fallback_news_data(query)

    # Keyword searches get video cards from YouTube when a key is configured;
    # without one (or on failure) the feed is just the NewsAPI articles.
    if query:
        videos = _fetch_youtube_videos(query, max(1, page_size // 2))
        if videos:
            articles = _interleave(articles, videos)
    return articles
