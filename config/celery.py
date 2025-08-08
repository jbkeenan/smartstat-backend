"""
Celery configuration for the Smart Thermostat project.

This module defines the Celery application instance and ties it into the
Django settings.  It also automatically discovers tasks from all installed
applications.

To run a Celery worker:

    celery -A config worker --loglevel=info

To run the beat scheduler (periodic tasks):

    celery -A config beat --loglevel=info

"""
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create the Celery application.
app = Celery('smart_thermostat')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.  Namespace='CELERY'
# means all celery-related configuration keys should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """A simple debugging task that prints the request's information."""
    print(f'Request: {self.request!r}')