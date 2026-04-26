#!/bin/bash
set -e

echo "Waiting for DB..."

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done

echo "DB ready"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Seeding merchants (safe)..."
python manage.py seed_merchants || true

echo "Starting Celery..."
celery -A app worker -l info &

echo "Starting server..."
exec gunicorn app.wsgi:application --bind 0.0.0.0:$PORT
