"""Test-suite compatibility shims.

Python 3.12 + Django 4.2.30 regression: ``django.template.context``
``BaseContext.__copy__`` implements the shallow copy as ``copy(super())``.
When the Django test client snapshots a render context (``store_rendered_templates``
copies the context after every template render), copying the copied ``super()``
proxy re-enters ``__copy__`` and blows the stack — but only once the render
call stack is already a few templates deep, so pages with several nested
``{% include %}`` / ``{% extends %}`` renders fail in tests with
``RecursionError`` while shallow pages pass.

Production is unaffected (render contexts are never ``copy()``-ed at runtime),
so this patch lives in the test path: ``apply_test_compat()`` is called at the
top of every test module.
"""


def apply_test_compat():
    from django.template import context as _django_context

    def _safe_base_context_copy(self):
        """Shallow-copy a context stack without the ``copy(super())`` trap."""
        duplicate = object.__new__(type(self))
        duplicate.dicts = self.dicts[:]
        return duplicate

    _django_context.BaseContext.__copy__ = _safe_base_context_copy
