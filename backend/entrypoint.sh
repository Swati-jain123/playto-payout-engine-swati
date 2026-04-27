#!/bin/bash
set -e

echo "🚀 Starting deployment..."

# 1. Wait for DB
until python -c "import django; from django.db import connections; django.setup(); connections['default'].cursor()" 2>/dev/null; do
  echo "DB not ready..."
  sleep 2
done

# 2. Migrations & Seeding
python manage.py migrate --noinput
python manage.py seed_merchants || echo "⚠️ Seeding skipped"

# 3. Start Celery (Modified for background stability)
echo "⚙️ Starting Celery Worker..."
# Use nohup and redirect logs to a file we can tail, or to the main output
nohup celery -A app worker --loglevel=info --concurrency=1 > celery_logs.txt 2>&1 &

echo "✅ Celery launched in background"

# 4. Start Gunicorn
echo "🌐 Starting Gguicorn..."
# We remove 'exec' so the script stays alive to monitor the background Celery
gunicorn app.wsgi:application \
  --bind 0.0.0.0:$PORT \
  --workers 1 \
  --timeout 120
