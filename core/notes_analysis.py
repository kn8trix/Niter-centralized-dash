"""Lightweight TF-IDF-style text analysis for the Notes Engine.

Extractive summarization + keyword extraction over note content. Pure Python
(no external NLP dependencies): term-frequency scoring with a stopword
filter (no corpus inverse-document-frequency — every note is scored in
isolation), matching the project's deterministic, dependency-free approach.

Kept in its own module (not ``core/views.py``) so the exact same functions
run inside the Huey background worker (``core.tasks``) without importing the
view layer.
"""

import re
from collections import Counter

# Lightweight English stopword list for the keyword + summary extractors.
_STOPWORDS = frozenset(
    ("the a an and or but if then else for with without of on in at by from to "
     "is are was were be been being have has had do does did will would can could "
     "should may might must this that these those it its i you he she we they them "
     "my your our their his her not no nor so as about into over under again further "
     "once here there when where why how all any both each few more most other some "
     "such only own same too very just also than up down out off because while "
     "during before after above below between through during against per via "
     "us am etc e g ie vs").split()
)


def note_tokens(text):
    """Lowercased alphanumeric tokens minus stopwords (min length 3)."""
    words = re.findall(r'[a-z0-9]+', (text or '').lower())
    return [w for w in words if w not in _STOPWORDS and len(w) >= 3]


def extract_keywords(content, limit=8):
    """Top ``limit`` keywords by term frequency (deterministic)."""
    tokens = note_tokens(content)
    ranked = Counter(tokens).most_common()
    return [word for word, _count in ranked[:limit]]


def count_sentences(content):
    """Number of non-empty sentences / paragraph lines in ``content``."""
    return len([s for s in re.split(r'(?<=[.!?])\s+|\n+', (content or '').strip()) if s.strip()])


def extract_summary(content, max_sentences=3):
    """Extractive summarization — score sentences by term frequency, keep the
    highest-scoring sentences in their original order."""
    text = (content or '').strip()
    if not text:
        return ''
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n+', text) if s.strip()]
    if len(sentences) <= max_sentences:
        return text

    freq = Counter(note_tokens(text))

    def score(sentence):
        tokens = note_tokens(sentence)
        if not tokens:
            return 0.0
        # Sum of term frequencies, dampened by length to favour dense sentences.
        return sum(freq.get(t, 0) for t in tokens) / (len(tokens) ** 0.6)

    scored = sorted(range(len(sentences)), key=lambda i: score(sentences[i]), reverse=True)
    picked = sorted(scored[:max_sentences])
    return ' '.join(sentences[i] for i in picked)
