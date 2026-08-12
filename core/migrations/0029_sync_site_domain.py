# Sync the django.contrib.sites ``Site`` row with the deployment hostname.
#
# allauth builds the Google OAuth redirect_uri from the Site row's ``domain``
# (``allauth.utils.build_absolute_uri`` → ``get_current_site``), NOT from the
# request host. A fresh database ships with the default ``example.com`` Site,
# which makes every social login fail with ``redirect_uri_mismatch`` even when
# SECURE_PROXY_SSL_HEADER / ACCOUNT_DEFAULT_HTTP_PROTOCOL are configured.
# This migration points Site id 1 at the real domain from the environment:
#
#   SITE_DOMAIN (explicit) > first usable ALLOWED_HOSTS entry > untouched
#
# On Render, ALLOWED_HOSTS auto-appends the platform + custom domain, so a
# bare ``python manage.py migrate`` fixes the row with no extra config.

import os

from django.db import migrations


def _pick_domain():
    explicit = os.environ.get('SITE_DOMAIN', '').strip()
    if explicit:
        return explicit
    allowed = os.environ.get('ALLOWED_HOSTS', '')
    for host in (h.strip() for h in allowed.split(',') if h.strip()):
        if host == '*':
            continue
        if host.startswith('.') or host.startswith('*.'):
            # Wildcard like .onrender.com — not a concrete callback host.
            continue
        if host in ('localhost', '127.0.0.1', '0.0.0.0', '[::1]'):
            # Local hosts are fine for dev but never the public Site domain;
            # keep searching for a real hostname first.
            continue
        return host
    return ''


def sync_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    domain = _pick_domain()
    if not domain:
        # Nothing usable in the environment — leave the row untouched rather
        # than overwrite a correctly-configured production Site with garbage.
        return
    Site.objects.update_or_create(
        pk=1,
        defaults={'domain': domain, 'name': domain},
    )


def reverse_site(apps, schema_editor):
    # Reversing is a no-op: the Site row is environment data, not schema.
    pass


class Migration(migrations.Migration):

    dependencies = [
        # Our own app's latest migration…
        ('core', '0028_researchthread_researchmessage'),
        # …and the sites app schema the Site row lives in.
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(sync_site, reverse_site),
    ]
