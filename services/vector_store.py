"""ChromaDB vector-store adapter — restricted to Study Corner + Research AI.

A thin, provider-isolating layer over an embedded ChromaDB ``PersistentClient``
(same conventions as ``services/openrouter.py`` / ``services/parser.py``):

* **Two collections only** — ``study_corner`` and ``research_ai``. Any other
  module name raises ``ValueError``, enforcing the "strictly these two modules"
  restriction in code.
* ``chromadb`` is imported **lazily**; if it is not installed (or the client
  cannot start), every method logs once and no-ops, so uploads and chat never
  break because the vector layer is unavailable — the same offline-friendly
  ethos as the OpenRouter/embeddings fallbacks.
* We compute embeddings ourselves (``services/embeddings.py``) and pass them to
  Chroma explicitly, so Chroma never downloads its default ONNX embedder.

Indexing and retrieval are gated by ``settings.VECTOR_INDEXING_ENABLED``.
"""

import logging

from django.conf import settings

from . import chunking, embeddings

logger = logging.getLogger(__name__)

# The ONLY modules permitted to use the vector store (Task 3 restriction).
STUDY_CORNER = 'study_corner'
RESEARCH_AI = 'research_ai'
ALLOWED_MODULES = (STUDY_CORNER, RESEARCH_AI)

# Cached client + a "we already tried and it failed" flag so a missing/broken
# chromadb install logs once and then silently no-ops.
_client = None
_client_unavailable = False


def _enabled():
    return getattr(settings, 'VECTOR_INDEXING_ENABLED', True)


def _validate_module(module):
    if module not in ALLOWED_MODULES:
        raise ValueError(
            'Vector store is restricted to %s (got %r).'
            % (' / '.join(ALLOWED_MODULES), module)
        )


def _get_client():
    """Return a cached Chroma ``PersistentClient``, or ``None`` if unavailable."""
    global _client, _client_unavailable
    if _client is not None:
        return _client
    if _client_unavailable:
        return None
    try:
        import chromadb
        from chromadb.config import Settings as ChromaSettings

        # chromadb 0.5.x logs noisy "Failed to send telemetry event …" errors
        # from its posthog client even with telemetry disabled — silence that
        # logger so it never clutters app logs (we set anonymized_telemetry too).
        logging.getLogger('chromadb.telemetry').setLevel(logging.CRITICAL)

        path = str(getattr(settings, 'VECTOR_STORE_PATH', 'vector_store'))
        _client = chromadb.PersistentClient(
            path=path,
            settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True),
        )
        return _client
    except Exception as exc:  # noqa: BLE001 — missing dep or startup failure
        _client_unavailable = True
        logger.warning(
            'Vector store unavailable (chromadb not usable: %s) — indexing/'
            'retrieval will no-op.', exc,
        )
        return None


def is_available():
    """True when indexing is enabled and a Chroma client is usable."""
    return bool(_enabled()) and _get_client() is not None


def _get_collection(client, module):
    return client.get_or_create_collection(
        name=module, metadata={'hnsw:space': 'cosine'}
    )


def index(module, source_id, text, metadata=None, owner=None):
    """Chunk → embed → upsert ``text`` for one source document.

    Returns the number of chunks indexed (``0`` when disabled/unavailable/empty).
    Existing chunks for the same ``source_id`` are cleared first, so
    re-indexing the same source is idempotent (no duplicate passages).
    """
    _validate_module(module)
    if not _enabled():
        return 0
    client = _get_client()
    if client is None:
        return 0

    text = (text or '').strip()
    if not text:
        return 0

    try:
        chunks = chunking.chunk_text(text)
        if not chunks:
            return 0
        vectors = embeddings.embed_texts(chunks)

        source_key = str(source_id)
        base_meta = dict(metadata or {})
        base_meta['module'] = module
        base_meta['source_id'] = source_key
        if owner is not None:
            base_meta['owner'] = str(owner)

        ids = ['%s:%s:%d' % (module, source_key, i) for i in range(len(chunks))]
        metadatas = []
        for i in range(len(chunks)):
            meta = dict(base_meta)
            meta['chunk_index'] = i
            metadatas.append(meta)

        collection = _get_collection(client, module)
        # Clear any prior chunks for this source (idempotent re-index).
        try:
            collection.delete(where={'source_id': source_key})
        except Exception:  # noqa: BLE001 — first index has nothing to delete
            pass
        collection.upsert(
            ids=ids, embeddings=vectors, documents=chunks, metadatas=metadatas
        )
        return len(chunks)
    except Exception as exc:  # noqa: BLE001 — indexing must never break upload
        logger.warning('Vector index failed for %s:%s — %s', module, source_id, exc)
        return 0


def query(module, text, k=4, owner=None):
    """Return up to ``k`` chunks most similar to ``text``.

    Each hit is ``{'text': str, 'metadata': dict, 'distance': float|None}``.
    Returns ``[]`` when disabled/unavailable/empty. When ``owner`` is given,
    results are filtered to that owner — Research AI is per-user; Study Corner
    is shared (pass ``owner=None``).
    """
    _validate_module(module)
    if not _enabled():
        return []
    client = _get_client()
    if client is None:
        return []

    text = (text or '').strip()
    if not text:
        return []

    try:
        collection = _get_collection(client, module)
        vector = embeddings.embed_text(text)
        where = {'owner': str(owner)} if owner is not None else None
        result = collection.query(
            query_embeddings=[vector],
            n_results=max(int(k), 1),
            where=where,
        )
        documents = (result.get('documents') or [[]])[0]
        metadatas = (result.get('metadatas') or [[]])[0]
        distances = (result.get('distances') or [[]])[0]

        hits = []
        for i, document in enumerate(documents):
            hits.append({
                'text': document,
                'metadata': metadatas[i] if i < len(metadatas) else {},
                'distance': distances[i] if i < len(distances) else None,
            })
        return hits
    except Exception as exc:  # noqa: BLE001 — retrieval must never break chat
        logger.warning('Vector query failed for %s — %s', module, exc)
        return []


def delete(module, source_id):
    """Remove every chunk for one source document. No-op when unavailable."""
    _validate_module(module)
    client = _get_client()
    if client is None:
        return
    try:
        collection = _get_collection(client, module)
        collection.delete(where={'source_id': str(source_id)})
    except Exception as exc:  # noqa: BLE001
        logger.warning('Vector delete failed for %s:%s — %s', module, source_id, exc)
