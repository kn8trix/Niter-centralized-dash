#!/usr/bin/env bash
# Remote production deploy — run on the server (typically via the GitHub
# Actions deploy workflow after `git pull`). Idempotent: safe to run by hand.
#
# Overridable via environment variables:
#   APP_DIR        app checkout directory (default: current directory)
#   VENV_DIR       Python virtualenv (default: $APP_DIR/venv)
#   SERVICE_NAME   systemd unit to reload (default: niter-centralized-dash)
set -euo pipefail

APP_DIR="${APP_DIR:-$(pwd)}"
VENV_DIR="${VENV_DIR:-$APP_DIR/venv}"
SERVICE_NAME="${SERVICE_NAME:-niter-centralized-dash}"

cd "$APP_DIR"

echo "==> [1/4] Installing Python dependencies"
"$VENV_DIR/bin/python" -m pip install -r requirements.txt

echo "==> [2/4] Applying database migrations"
"$VENV_DIR/bin/python" manage.py migrate --noinput

echo "==> [3/4] Collecting static assets (WhiteNoise)"
"$VENV_DIR/bin/python" manage.py collectstatic --noinput

echo "==> [4/4] Reloading $SERVICE_NAME"
# Reload prefers plain systemctl but falls back to `sudo -n` so the deploy
# SSH user works with either passwordless root or passwordless sudo.
if command -v systemctl >/dev/null 2>&1 && systemctl is-active --quiet "$SERVICE_NAME"; then
    if systemctl reload "$SERVICE_NAME" 2>/dev/null || sudo -n systemctl reload "$SERVICE_NAME" 2>/dev/null; then
        echo "    reloaded $SERVICE_NAME"
    elif systemctl restart "$SERVICE_NAME" 2>/dev/null || sudo -n systemctl restart "$SERVICE_NAME" 2>/dev/null; then
        echo "    restarted $SERVICE_NAME"
    else
        echo "    could not reload/restart — check permissions on '$SERVICE_NAME'."
    fi
else
    echo "    systemd unit '$SERVICE_NAME' not active — skipping reload (start it manually)."
fi

echo "==> Deploy complete"
