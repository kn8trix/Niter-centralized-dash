"""Character-based text chunking for the vector-store indexing pipeline.

Splits extracted document text into overlapping windows before embedding so a
single long PDF/note becomes several retrievable passages. Dependency-free
(pure Python) — the same ethos as ``services/parser.py``: the RAG pipeline must
work with nothing installed beyond the standard library.
"""

DEFAULT_CHUNK_SIZE = 1000
DEFAULT_OVERLAP = 150

# When the hard character boundary lands mid-word, we look back at most this
# many characters for a natural break (whitespace/newline) so chunks end on a
# word rather than slicing one in half.
_BACKTRACK_WINDOW = 120


def chunk_text(text, size=DEFAULT_CHUNK_SIZE, overlap=DEFAULT_OVERLAP):
    """Split ``text`` into overlapping character windows.

    Returns a list of non-empty, stripped chunks of roughly ``size`` characters
    each, consecutive chunks sharing ``overlap`` characters of context. When a
    window would cut through a word, the split point is nudged back to the last
    whitespace within :data:`_BACKTRACK_WINDOW` characters so chunks stay
    readable. Returns ``[]`` for empty input.
    """
    if not text:
        return []
    text = text.strip()
    if not text:
        return []

    size = max(int(size), 1)
    overlap = max(min(int(overlap), size - 1), 0)

    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + size, length)
        # Nudge the boundary back to a word break when we're not at the very end.
        if end < length:
            floor = max(end - _BACKTRACK_WINDOW, start + 1)
            boundary = max(text.rfind(' ', floor, end), text.rfind('\n', floor, end))
            if boundary > start:
                end = boundary

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= length:
            break
        # Advance, keeping ``overlap`` characters of trailing context.
        start = max(end - overlap, start + 1)

    return chunks
