#!/bin/bash
set -e

echo "Waiting for DB..."

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done

echo "DB ready"

# Run migrations only when enabled
if [ "$RUN_MIGRATIONS" = "true" ]; then
  echo "Running migrations..."
  python manage.py migrate --noinput

  echo "Seeding merchants..."
  python manage.py seed_merchants
fi

echo "Starting Celery Worker..."

# Start Celery in background
celery -A app worker -l info --concurrency=2 &

echo "Starting Django server..."

# Start Gunicorn (MAIN PROCESS - must stay alive)
exec gunicorn app.wsgi:application --bind 0.0.0.0:$PORT
