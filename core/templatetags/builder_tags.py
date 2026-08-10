"""Template tags for the Website Builder.

Usage in a template::

    {% load builder_tags %}
    {% render_block page_slug="dashboard" element_id="hero-title" default_text="Welcome" %}

Renders the saved ``ContentBlock`` for the matching page and element:

  * ``html`` blocks render their saved ``content_html`` directly,
  * structured blocks (``faq`` / ``stats`` / ``testimonials`` / ``cta``)
    are rendered through the matching partial in ``templates/builder/blocks/``
    with their ``content_json`` data,
  * a missing/blank block, an unknown type, or a partial that fails to load
    falls back to ``default_text`` (a broken block never 500s the page).
"""

import logging
import re

from django import template
from django.template.loader import get_template
from django.utils.html import mark_safe

from core.models import ContentBlock

register = template.Library()
logger = logging.getLogger(__name__)

# Structured block type → template partial (kept in sync with
# ContentBlock.BLOCK_TYPE_CHOICES / BLOCK_SCHEMAS).
_BLOCK_PARTIALS = {
    'faq': 'builder/blocks/faq_accordion.html',
    'stats': 'builder/blocks/stats_grid.html',
    'testimonials': 'builder/blocks/testimonial_slider.html',
    'cta': 'builder/blocks/cta_section.html',
}


def render_block_html(block, default_text=""):
    """Render a ContentBlock to its final HTML (partial or raw content).

    ``block`` may be ``None`` (missing block). Any failure while resolving or
    rendering the partial — including a non-dict ``content_json`` saved by
    mistake — falls back to the raw ``content_html`` and then to
    ``default_text``. Rendering a page must never raise because of one block.
    """
    if block is None:
        return default_text

    partial = _BLOCK_PARTIALS.get(block.block_type)
    if partial:
        data = block.content_json or {}
        if not data:
            # Structured block with no data yet behaves like an empty block.
            return block.content_html if block.content_html.strip() else default_text
        if not isinstance(data, dict):
            # A JSONField row could hold a list/string if someone edited it in
            # the admin by hand — treat it as malformed and fall back.
            logger.warning(
                'Builder block %s (%s): content_json is %s, not a dict',
                block.element_id, block.block_type, type(data).__name__,
            )
            return block.content_html if block.content_html.strip() else default_text
        try:
            tpl = get_template(partial)
        except template.TemplateDoesNotExist:
            logger.warning('Builder partial missing for %s: %s', block.block_type, partial)
            tpl = None
        if tpl is not None:
            # Normalize so the partials can iterate ``data.items`` safely: a
            # missing ``items`` key would otherwise resolve to the dict's
            # built-in bound method in Django templates and silently render
            # nothing (or crash on iteration) instead of hitting ``{% empty %}``.
            normalized = dict(data)
            normalized.setdefault('items', [])
            # The testimonial slider gates its controls on the number of
            # actually renderable slides (quote-bearing items), not raw count.
            # Passed as a top-level context var because Django's smartif cannot
            # evaluate a dotted variable inside {% if %} (it would 500).
            show_controls = False
            if block.block_type == 'testimonials':
                slide_count = sum(
                    1 for item in normalized['items']
                    if isinstance(item, dict) and item.get('quote')
                )
                show_controls = slide_count > 1
            try:
                return tpl.render({
                    'block': block,
                    'data': normalized,
                    'show_controls': show_controls,
                })
            except Exception:
                # A malformed block (e.g. bad JSON data) must not break the page.
                logger.exception('Failed to render builder block %s (%s)', block.element_id, block.block_type)

    if block.content_html.strip():
        return block.content_html
    return default_text


# URL schemes permitted in CTA ``href`` attributes. Mirrors the scheme
# allow-list the block HTML sanitizer applies to ``content_html`` links, so
# ``content_json`` URLs get the same defense-in-depth treatment.
_SAFE_URL_SCHEMES = frozenset({'http', 'https', 'mailto', 'tel', 'ftp'})


@register.filter
def safe_url(value):
    """Return a link-safe URL: allowed schemes and relative/# paths pass
    through; anything else (e.g. ``javascript:``) is replaced with ``#``."""
    value = (value or '').strip()
    if not value or value.startswith('#') or value.startswith('/') or value.startswith('//'):
        return value
    scheme = re.match(r'^([a-z][a-z0-9+.-]*):', value.lower())
    if scheme and scheme.group(1) not in _SAFE_URL_SCHEMES:
        return '#'
    return value


@register.simple_tag
def render_block(page_slug, element_id, default_text=""):
    """Render a ContentBlock, falling back to ``default_text`` on any failure."""
    block = (
        ContentBlock.objects
        .filter(page__slug=page_slug, element_id=element_id)
        .first()
    )
    return mark_safe(render_block_html(block, default_text))
