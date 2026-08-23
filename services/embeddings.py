"""Text embeddings for the vector-store RAG pipeline.

``embed_texts(texts)`` returns one dense vector per input string. Two backends,
selected by configuration — mirroring the ``OPENROUTER_ENABLED`` pattern:

* **API backend** — when ``EMBEDDINGS_API_KEY`` is set, POST to an
  OpenAI-compatible ``/embeddings`` endpoint (``EMBEDDINGS_API_URL`` +
  ``EMBEDDINGS_MODEL``) and return the provider's vectors.
* **Offline fallback** — otherwise a deterministic, dependency-free hashing
  vectorizer (signed feature hashing + sub-linear term frequency, L2
  normalized). Low-but-usable retrieval quality with zero configuration and no
  network, so Study Corner / Research AI indexing works out of the box. Swap in
  sentence-transformers later by editing only this file.

The offline vectors are :data:`EMBEDDING_DIM`-dimensional. A single deployment
uses one backend consistently, so a Chroma collection never mixes dimensions;
if you switch backends after indexing, rebuild the store (dims must match).
"""

import hashlib
import logging
import math
import re

from django.conf import settings

logger = logging.getLogger(__name__)

# Dimensionality of the offline hashing embeddings. 384 matches the popular
# all-MiniLM-L6-v2 sentence-transformer, easing a future swap.
EMBEDDING_DIM = 384

# Hard cap on a single embeddings API call (seconds).
_API_TIMEOUT_SECONDS = 20

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _get(name, default=''):
    return getattr(settings, name, default)


def is_api_enabled():
    """True when an embeddings API key is configured (use the live provider)."""
    return bool(_get('EMBEDDINGS_API_KEY', ''))


def embed_texts(texts):
    """Return a list of embedding vectors, one per string in ``texts``.

    Never raises for provider/transport reasons: if the API backend is
    configured but fails, it logs and falls back to the deterministic offline
    embeddings so indexing/retrieval degrade in quality rather than break.
    """
    items = [t if isinstance(t, str) else ('' if t is None else str(t)) for t in (texts or [])]
    if not items:
        return []

    if is_api_enabled():
        try:
            return _embed_via_api(items)
        except Exception as exc:  # noqa: BLE001 — must never break the caller
            logger.warning('Embeddings API failed (%s) — using offline fallback.', exc)

    return [_hash_embed(text) for text in items]


def embed_text(text):
    """Convenience: embed a single string, returning one vector."""
    vectors = embed_texts([text])
    return vectors[0] if vectors else _hash_embed('')


def _embed_via_api(texts):
    """POST ``texts`` to an OpenAI-compatible embeddings endpoint."""
    import requests

    url = _get('EMBEDDINGS_API_URL', '') or 'https://api.openai.com/v1/embeddings'
    model = _get('EMBEDDINGS_MODEL', '') or 'text-embedding-3-small'
    headers = {
        'Authorization': 'Bearer %s' % _get('EMBEDDINGS_API_KEY', ''),
        'Content-Type': 'application/json',
    }
    response = requests.post(
        url,
        headers=headers,
        json={'model': model, 'input': texts},
        timeout=_API_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    data = response.json()
    rows = sorted(data['data'], key=lambda row: row.get('index', 0))
    return [list(row['embedding']) for row in rows]


def _hash_embed(text):
    """Deterministic signed-hashing bag-of-words embedding (L2 normalized)."""
    vector = [0.0] * EMBEDDING_DIM
    counts = {}
    for token in _TOKEN_RE.findall((text or '').lower()):
        counts[token] = counts.get(token, 0) + 1

    for token, count in counts.items():
        digest = hashlib.md5(token.encode('utf-8')).digest()
        bucket = int.from_bytes(digest[:4], 'big') % EMBEDDING_DIM
        sign = 1.0 if digest[4] & 1 else -1.0
        # Sub-linear term frequency dampens very frequent tokens.
        vector[bucket] += sign * (1.0 + math.log(count))

    norm = math.sqrt(sum(value * value for value in vector))
    if norm > 0.0:
        vector = [value / norm for value in vector]
    return vector
