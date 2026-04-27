#!/bin/bash
set -e

echo "🚀 Starting deployment..."

# ---------------------------
# 1. Wait for DB connection
# ---------------------------
echo "⏳ Waiting for database..."

# Using a simpler check that doesn't require dbshell permissions
until python -c "import sys; import django; from django.db import connections; django.setup(); connections['default'].cursor()" 2>/dev/null; do
  echo "DB not ready yet..."
  sleep 2
done

echo "✅ Database is reachable"

# ---------------------------
# 2. Run migrations
# ---------------------------
echo "📦 Running migrations..."
python manage.py migrate --noinput

# ---------------------------
# 3. Seed data
# ---------------------------
echo "🌱 Seeding merchants..."
python manage.py seed_merchants || echo "⚠️ Seeding skipped"

# ---------------------------
# 4. Start Celery (Background)
# ---------------------------
echo "⚙️ Starting Celery Worker..."

# --concurrency=1 is CRITICAL for free tier/single-instance setups to save RAM
# We redirect logs to stdout so you can see them in your dashboard
celery -A app worker --loglevel=info --concurrency=1 &

# Save the PID just in case, though we won't 'exec' over it now
CELERY_PID=$!
echo "Celery started with PID: $CELERY_PID"

# ---------------------------
# 5. Start server
# ---------------------------
echo "🌐 Starting Gunicorn..."

# IMPORTANT: Removed 'exec'. By running gunicorn normally, 
# the bash script remains alive as a parent to the Celery process.
gunicorn app.wsgi:application \
  --bind 0.0.0.0:$PORT \
  --workers 2 \
  --timeout 120

# If Gunicorn ever exits, we want the script to exit
exit $?
