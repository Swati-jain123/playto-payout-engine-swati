#!/bin/bash
set -e

echo "🚀 Starting deployment..."

# ---------------------------
# 1. Wait for DB connection
# ---------------------------
echo "⏳ Waiting for database..."

until python manage.py dbshell -c "SELECT 1" 2>/dev/null; do
  echo "DB not ready yet..."
  sleep 2
done

echo "✅ Database is reachable"

# ---------------------------
# 2. Run migrations (SAFE)
# ---------------------------
echo "📦 Running migrations..."

python manage.py migrate --noinput

echo "✅ Migrations completed"

# ---------------------------
# 3. Seed data (SAFE mode)
# ---------------------------
echo "🌱 Seeding merchants..."

python manage.py seed_merchants || echo "⚠️ Seeding skipped or already done"

echo "✅ Seeding step completed"

# ---------------------------
# 4. Start Celery (optional safe)
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
