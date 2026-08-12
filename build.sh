#!/usr/bin/env bash
# Render build script — invoked by the render.yaml Blueprint (`buildCommand: ./build.sh`).
# Installs dependencies, collects static assets (WhiteNoise), applies migrations,
# and seeds the demo users (admin/student) so every environment has working
# login credentials from the first deploy.
#
# - set -o errexit: any failing step aborts the build immediately.
# - set -o pipefail: a failure inside a pipeline also aborts the build.
# - RENDER_BUILD=true: settings.py uses a throwaway SECRET_KEY placeholder for
#   the build phase only (collectstatic/migrate/seed run before the service's
#   generated secret is injected); the runtime start command never sets it.
set -o errexit
set -o pipefail

# Pick the Python interpreter. Render's build image provides `python`; a local
# checkout may only expose `python3` (or a virtualenv). Prefer the venv when
# present so `./build.sh` works in a local dev environment too.
if [ -x "venv/bin/python" ]; then
    PYTHON="venv/bin/python"
elif command -v python >/dev/null 2>&1; then
    PYTHON="python"
else
    PYTHON="python3"
fi
echo "==> Using interpreter: $PYTHON"

# Old pip on Python 3.12 can mis-resolve dependency ranges; upgrade it first.
echo "==> Upgrading pip"
"$PYTHON" -m pip install --upgrade pip

echo "==> Installing Python dependencies"
"$PYTHON" -m pip install -r requirements.txt

echo "==> Collecting static assets (WhiteNoise -> staticfiles/)"
RENDER_BUILD=true "$PYTHON" manage.py collectstatic --noinput

# Migrations run against whichever database is configured — SUPABASE_DB_URL when
# set, otherwise DATABASE_URL (the Render-managed Postgres). The render.yaml
# releaseCommand also runs `migrate --noinput` idempotently before the new
# release serves, so an already-migrated database is a no-op here.
echo "==> Applying database migrations"
RENDER_BUILD=true "$PYTHON" manage.py migrate --noinput

# Seed the demo accounts (idempotent — existing users are never touched):
# admin/admin123 (superuser + staff) and student/student123.
echo "==> Seeding demo users"
RENDER_BUILD=true "$PYTHON" manage.py seed_demo_users

echo "==> Build complete"
