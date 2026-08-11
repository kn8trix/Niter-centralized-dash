"""Shared sanitizer for Website Builder block content (defense-in-depth).

This module is the single source of truth for the builder's HTML/CSS
allow-lists. It is used in two places so stored content is always neutralized
before it reaches a browser, even if it was written before the sanitizer
existed or hand-edited in the admin:

  * **Save time** — ``core.views.save_content_block`` / ``save_page_css``
    sanitize author input before it is stored.
  * **Render time** — ``core.templatetags.builder_tags.render_block_html``
    re-sanitizes raw ``content_html`` and ``editable_page_view`` re-sanitizes
    ``custom_css``, so a never-sanitized row still renders clean.

The HTML sanitizer is built on **bleach** (a battle-tested allow-list
sanitizer) configured with the builder's existing tag/attribute allow-lists.
``script``/``style`` elements are pre-dropped *in full* (content included):
bleach strips disallowed tags but would otherwise keep their text, which would
turn an injected ``<script>alert(1)</script>`` into visible ``alert(1)`` text
on the page instead of removing it.

The builder API is superuser-only, so this is belt-and-braces on top of the
existing trust model.
"""

import re

import bleach

ALLOWED_TAGS = frozenset({
    'p', 'br', 'hr', 'div', 'span',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'strong', 'b', 'em', 'i', 'u', 's', 'mark',
    'a', 'img', 'ul', 'ol', 'li', 'blockquote', 'code', 'pre',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
})

VOID_TAGS = frozenset({'br', 'hr', 'img'})

# Per-tag attribute allow-list (``style``, ``on*`` and anything else is dropped).
ALLOWED_ATTRS = {
    'a': {'href', 'title', 'target'},
    'img': {'src', 'alt', 'title', 'width', 'height'},
    'code': {'class'},
    'pre': {'class'},
    'div': {'class'},
    'span': {'class'},
    'th': {'colspan', 'rowspan'},
    'td': {'colspan', 'rowspan'},
}

SAFE_URL_SCHEMES = frozenset({'http', 'https', 'mailto', 'tel', 'ftp'})

# Whole-element drop for <script>/<style> (see module docstring). The regex is
# deliberately tolerant of attribute casing and whitespace inside the tags.
_SCRIPT_STYLE_RE = re.compile(
    r'<\s*(script|style)\b[^>]*>.*?<\s*/\s*\1\s*>',
    re.DOTALL | re.IGNORECASE,
)


def sanitize_html(raw_html):
    """Return ``raw_html`` with all non-allow-listed tags/attributes removed.

    Implemented with bleach's allow-list sanitizer using the builder's
    ``ALLOWED_TAGS`` / ``ALLOWED_ATTRS`` / ``SAFE_URL_SCHEMES``. ``script`` /
    ``style`` blocks are dropped entirely first; everything else keeps its
    text (safely escaped) minus disallowed tags, attributes and URL schemes.
    """
    if not raw_html:
        return ''
    without_script_style = _SCRIPT_STYLE_RE.sub('', raw_html)
    return bleach.clean(
        without_script_style,
        tags=ALLOWED_TAGS,
        attributes={tag: list(attrs) for tag, attrs in ALLOWED_ATTRS.items()},
        protocols=SAFE_URL_SCHEMES,
        strip=True,
    )


# custom_css is injected with ``|safe`` inside a <style> tag on the live page,
# so strip anything that could break out of it: both closing and opening
# ``<style>``/``<script>`` tokens plus HTML comments. CSS never legitimately
# contains ``<``, so these matches are always hostile.
_UNSAFE_CSS_PATTERNS = (
    re.compile(r'</\s*style', re.IGNORECASE),
    re.compile(r'<\s*style', re.IGNORECASE),
    re.compile(r'</\s*script', re.IGNORECASE),
    re.compile(r'<\s*script', re.IGNORECASE),
    re.compile(r'<!--'),
)


def sanitize_css(raw_css):
    """Light guard for custom_css: remove <style>/<script> break-out tokens."""
    if not raw_css:
        return ''
    css = raw_css
    for pattern in _UNSAFE_CSS_PATTERNS:
        css = pattern.sub('', css)
    return css
