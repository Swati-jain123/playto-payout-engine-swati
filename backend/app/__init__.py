from __future__ import absolute_import, unicode_literals
from celery import Celery
import os

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# Create Celery app
app = Celery('app')

# Load config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')