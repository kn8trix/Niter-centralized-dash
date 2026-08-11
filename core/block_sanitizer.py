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

The builder API is superuser-only, so this is belt-and-braces on top of the
existing trust model: a strict allow-list keeps pasted content free of script
tags, event handlers, and inline-style / ``javascript:`` URL injection.
"""

import html
import html.parser
import re

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


def _is_safe_url(value):
    """Allow relative/absolute links but reject dangerous URL schemes."""
    stripped = (value or '').strip().lower()
    if not stripped or stripped.startswith('#') or stripped.startswith('//'):
        return True
    scheme = re.match(r'^([a-z][a-z0-9+.-]*):', stripped)
    if not scheme:
        return True  # relative path such as /dashboard/ or images/x.png
    return scheme.group(1) in SAFE_URL_SCHEMES


class _BlockHtmlSanitizer(html.parser.HTMLParser):
    """Rebuild input HTML keeping only allow-listed tags and attributes.

    Content inside a disallowed element (e.g. ``<script>``) is dropped
    entirely rather than being leaked as text. Fail-safe: an unclosed
    disallowed tag swallows the rest of the document, which can only
    ever lose content (never allow it through).
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._out = []
        self._skip_depth = 0

    def _safe_attrs(self, tag, attrs):
        allowed = ALLOWED_ATTRS.get(tag, frozenset())
        for key, value in attrs:
            if key not in allowed or key.lower().startswith('on'):
                continue
            if key in ('href', 'src') and not _is_safe_url(value):
                continue
            yield key, html.escape(value, quote=True)

    def _emit_start(self, tag, attrs, self_closing):
        parts = ['<%s' % tag]
        for key, value in self._safe_attrs(tag, attrs):
            parts.append(' %s="%s"' % (key, value))
        parts.append(' />' if self_closing else '>')
        self._out.append(''.join(parts))

    def handle_starttag(self, tag, attrs):
        if tag not in ALLOWED_TAGS:
            self._skip_depth += 1
            return
        if not self._skip_depth:
            self._emit_start(tag, attrs, self_closing=False)

    def handle_startendtag(self, tag, attrs):
        # XHTML-style self-closing tags such as <img /> / <br />
        if tag in ALLOWED_TAGS and not self._skip_depth:
            self._emit_start(tag, attrs, self_closing=True)

    def handle_endtag(self, tag):
        if tag not in ALLOWED_TAGS:
            if self._skip_depth:
                self._skip_depth -= 1
            return
        if not self._skip_depth and tag not in VOID_TAGS:
            self._out.append('</%s>' % tag)

    def handle_data(self, data):
        if not self._skip_depth:
            self._out.append(html.escape(data))

    def handle_comment(self, data):
        pass  # drop comments

    def handle_decl(self, decl):
        pass  # drop <!DOCTYPE ...>

    def handle_pi(self, data):
        pass  # drop <?...?>


def sanitize_html(raw_html):
    """Return ``raw_html`` with all non-allow-listed tags/attributes removed."""
    if not raw_html:
        return ''
    parser = _BlockHtmlSanitizer()
    parser.feed(raw_html)
    parser.close()
    return ''.join(parser._out)


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
