"""Permission guards for the Super Admin Website Builder."""

from functools import wraps

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def change_editablepage_required(view_func=None, login_url=None):
    """Restrict a view to users holding the builder's change_editablepage permission.

    Mirrors ``superuser_required``'s UX while gating on the permission instead
    of the superuser flag (superusers pass implicitly — they hold every
    permission):

    - Anonymous visitors are redirected to the login page (with the usual
      ``?next=`` parameter preserved by ``user_passes_test``).
    - Authenticated users without the permission receive a 403 Forbidden
      response instead of a redirect, so they never bounce between the
      page and the login form.

    Usable as ``@change_editablepage_required`` or
    ``@change_editablepage_required(login_url='/custom-login/')``.
    """
    login_url = login_url or settings.LOGIN_URL

    def _has_perm(user):
        return bool(user.is_authenticated and user.has_perm('core.change_editablepage'))

    # user_passes_test performs the auth/permission check and redirects
    # failing users to the login page.
    _redirect_to_login = user_passes_test(_has_perm, login_url=login_url)

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and not request.user.has_perm('core.change_editablepage'):
                # Logged in but lacking the builder permission: a redirect
                # would loop straight back, so fail closed with 403 Forbidden.
                raise PermissionDenied
            return _redirect_to_login(view_func)(request, *args, **kwargs)

        return _wrapped_view

    if view_func:
        return decorator(view_func)
    return decorator

def admin_required(view_func=None, login_url=None):
    """Restrict a view to portal admins (staff or superuser).

    Mirrors ``superuser_required`` but admits the whole ``admin`` role
    (``is_staff`` OR ``is_superuser``) — the staff flag already gates every
    admin dashboard in the project, so this is the canonical RBAC guard for
    the ``/dashboard/admin/*`` area.

    - Anonymous visitors are redirected to the login page.
    - Authenticated non-admins (students / club managers) get a 403 Forbidden
      response so they never bounce between the page and the login form.
    """
    login_url = login_url or settings.LOGIN_URL

    def _is_admin(user):
        return bool(user.is_authenticated and (user.is_staff or user.is_superuser))

    _redirect_to_login = user_passes_test(_is_admin, login_url=login_url)

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and not (request.user.is_staff or request.user.is_superuser):
                raise PermissionDenied
            return _redirect_to_login(view_func)(request, *args, **kwargs)

        return _wrapped_view

    if view_func:
        return decorator(view_func)
    return decorator

def club_access_required(view_func=None, login_url=None):
    """Restrict a view to staff/superusers OR active club-account holders.

    The club workspace (``/clubs/manage/``) is the landing area for the
    ``club`` role, so it must admit club managers as well as staff. Anonymous
    visitors are redirected to login; authenticated users with neither a staff
    flag nor an active ``ClubAccount`` get a 403.
    """
    login_url = login_url or settings.LOGIN_URL

    def _has_club_access(user):
        if not user.is_authenticated:
            return False
        if user.is_staff or user.is_superuser:
            return True
        account = getattr(user, 'club_account', None)
        return bool(account is not None and account.is_active)

    _redirect_to_login = user_passes_test(_has_club_access, login_url=login_url)

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and not _has_club_access(request.user):
                raise PermissionDenied
            return _redirect_to_login(view_func)(request, *args, **kwargs)

        return _wrapped_view

    if view_func:
        return decorator(view_func)
    return decorator


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
