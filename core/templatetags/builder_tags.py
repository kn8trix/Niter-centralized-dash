"""Template tags for the Website Builder.

Usage in a template::

    {% load builder_tags %}
    {% render_block page_slug="dashboard" element_id="hero-title" default_text="Welcome" %}

Renders the saved ``ContentBlock.content_html`` for the matching page and
element, or the ``default_text`` when the block is missing or empty.
"""

from django import template
from django.utils.html import mark_safe

from core.models import ContentBlock

register = template.Library()


@register.simple_tag
def render_block(page_slug, element_id, default_text=""):
    """Render a ContentBlock's HTML, falling back to ``default_text``."""
    block = (
        ContentBlock.objects
        .filter(page__slug=page_slug, element_id=element_id)
        .first()
    )
    if block is not None and block.content_html.strip():
        return mark_safe(block.content_html)
    return mark_safe(default_text)
