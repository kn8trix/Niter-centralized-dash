#!/usr/bin/env bash
# Render build script — invoked by the render.yaml Blueprint (`buildCommand: ./build.sh`).
# Installs dependencies and collects static assets (WhiteNoise). Database
# migrations intentionally run in the release phase (`releaseCommand` in
# render.yaml): the release command executes after the build succeeds and
# BEFORE the new version starts serving, so a failed migration aborts the
# deploy while the current release keeps serving traffic.
#
# - set -o errexit: any failing step aborts the build immediately.
# - set -o pipefail: a failure inside a pipeline also aborts the build.
# - RENDER_BUILD=true: settings.py uses a throwaway SECRET_KEY placeholder for
#   the build phase only (collectstatic runs before the service's generated
#   secret is injected); the runtime start command never sets it.
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

echo "==> Build complete"
