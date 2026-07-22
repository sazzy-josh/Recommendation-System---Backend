#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating admin account..."
python manage.py create_admin

echo "Seeding departments and courses..."
python manage.py seed_courses

echo "Starting server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120
