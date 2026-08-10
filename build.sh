#!/usr/bin/env bash
# Render build script — invoked by the render.yaml Blueprint (`buildCommand: ./build.sh`).
# Installs dependencies, collects static assets (WhiteNoise), and applies
# database migrations before the web service starts.
set -o errexit

echo "==> Installing Python dependencies"
python -m pip install -r requirements.txt

echo "==> Collecting static assets (WhiteNoise -> staticfiles/)"
python manage.py collectstatic --noinput

echo "==> Applying database migrations"
python manage.py migrate

echo "==> Build complete"
