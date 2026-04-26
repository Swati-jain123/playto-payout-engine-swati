#!/bin/bash
set -e

echo "Waiting for DB..."

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done

echo "DB ready"

# Only run migrate/seed when starting server (NOT for CLI commands)
if [ "$RUN_MIGRATIONS" = "true" ] && [ "$1" = "gunicorn" ]; then
  echo "Running migrations..."
  python manage.py migrate --noinput

  echo "Seeding merchants..."
  python manage.py seed_merchants
fi

echo "Starting service..."
exec "$@"