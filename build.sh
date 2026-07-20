#!/usr/bin/env bash
set -e

pip install -r requirements.txt
DJANGO_SETTINGS_MODULE=config.settings.production python manage.py collectstatic --no-input
DJANGO_SETTINGS_MODULE=config.settings.production python manage.py migrate
DJANGO_SETTINGS_MODULE=config.settings.production python manage.py seed_courses
