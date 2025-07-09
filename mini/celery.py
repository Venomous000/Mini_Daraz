import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mini.settings')

app = Celery('mini')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks across all apps (like wishlist.tasks)
app.autodiscover_tasks()