#!/usr/bin/env bash
# Render build script: install deps, collect static files, apply migrations.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input --clear
python manage.py migrate
