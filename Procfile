web: gunicorn app.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 120
worker: celery -A app worker --loglevel=info --concurrency=1
