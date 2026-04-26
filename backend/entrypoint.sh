#!/bin/bash
set -e

echo "🚀 Starting deployment..."

# ---------------------------
# 1. Wait for DB (safe check)
# ---------------------------
echo "⏳ Waiting for DB..."

until python manage.py check --database default 2>/dev/null; do
  echo "DB not ready yet..."
  sleep 2
done

echo "✅ DB is ready"

# ---------------------------
# 2. Run migrations (CRITICAL FIXED)
# ---------------------------
echo "📦 Running migrations..."

python manage.py migrate auth --noinput
python manage.py migrate contenttypes --noinput
python manage.py migrate sessions --noinput
python manage.py migrate admin --noinput
python manage.py migrate --noinput

echo "✅ Migrations completed"

# ---------------------------
# 3. Seed data (DO NOT HIDE ERRORS)
# ---------------------------
echo "🌱 Seeding merchants..."

python manage.py seed_merchants

echo "✅ Seeding completed"

# ---------------------------
# 4. Start Celery (safe background)
# ---------------------------
echo "⚙️ Starting Celery..."

celery -A app worker -l info --loglevel=info &
CELERY_PID=$!

echo "Celery PID: $CELERY_PID"

# ---------------------------
# 5. Start server
# ---------------------------
echo "🌐 Starting Gunicorn..."

exec gunicorn app.wsgi:application \
  --bind 0.0.0.0:$PORT \
  --workers 2 \
  --timeout 120
