"""Plain-text extraction for research reference documents.

Converts uploaded PDF/DOCX files into prompt-ready plain text that the
Research AI endpoint feeds into the OpenRouter system prompt as the
"Current Reference" context. The extraction libraries (``pypdf`` /
``python-docx``) are imported lazily inside each function so a missing
optional dependency degrades to ``None`` (the query still runs, just without
the document context) instead of crashing the endpoint.
"""

import io
import logging

logger = logging.getLogger(__name__)


def extract_document_text(upload):
    """Extract plain text from an uploaded reference file.

    ``upload`` is a Django ``UploadedFile`` (or any object exposing ``name``
    and ``file``/``read``). Returns the extracted text, or ``None`` when the
    format is unsupported or the text could not be parsed.
    """
    if upload is None:
        return None
    name = (getattr(upload, 'name', '') or '').lower()
    try:
        if name.endswith('.pdf'):
            return extract_pdf_text(upload)
        if name.endswith('.docx'):
            return extract_docx_text(upload)
    except Exception as exc:  # Extraction must never break the query flow.
        logger.warning('Document text extraction failed for %s: %s', name, exc)
        return None
    return None


def extract_pdf_text(upload):
    """Extract text from a PDF file using ``pypdf`` (lazy import)."""
    try:
        from pypdf import PdfReader
    except ImportError:
        logger.warning('pypdf is not installed — PDF extraction unavailable.')
        return None

    reader = PdfReader(io.BytesIO(upload.read()))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or '')
    return '\n\n'.join(pages).strip() or None


def extract_docx_text(upload):
    """Extract paragraph text from a .docx file using ``python-docx``."""
    try:
        from docx import Document
    except ImportError:
        logger.warning('python-docx is not installed — DOCX extraction unavailable.')
        return None

    document = Document(io.BytesIO(upload.read()))
    paragraphs = [p.text for p in document.paragraphs if p.text and p.text.strip()]
    return '\n'.join(paragraphs).strip() or None
