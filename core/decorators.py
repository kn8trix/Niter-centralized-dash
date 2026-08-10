"""Permission guards for the Super Admin Website Builder."""

from functools import wraps

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def superuser_required(view_func=None, login_url=None):
    """Restrict a view to authenticated superusers.

    - Anonymous visitors are redirected to the login page (with the usual
      ``?next=`` parameter preserved by ``user_passes_test``).
    - Authenticated non-superusers (staff or students) receive a 403
      Forbidden response instead of a redirect, so they never bounce
      between the page and the login form.

    Usable as ``@superuser_required`` or
    ``@superuser_required(login_url='/custom-login/')``.
    """
    login_url = login_url or settings.LOGIN_URL

    def _is_superuser(user):
        return bool(user.is_authenticated and user.is_superuser)

    # user_passes_test performs the authentication/superuser check and
    # redirects failing users to the login page.
    _redirect_to_login = user_passes_test(_is_superuser, login_url=login_url)

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and not request.user.is_superuser:
                # Logged in but lacking superuser rights: a redirect would
                # loop straight back, so fail closed with 403 Forbidden.
                raise PermissionDenied
            return _redirect_to_login(view_func)(request, *args, **kwargs)

        return _wrapped_view

    if view_func:
        return decorator(view_func)
    return decorator
