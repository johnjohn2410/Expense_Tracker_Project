import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Expense_Tracker_Project.settings')

app = Celery('Expense_Tracker_Project')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Celery Beat Schedule for periodic tasks
app.conf.beat_schedule = {
    'process-pending-imports': {
        'task': 'tracker.tasks.process_pending_imports',
        'schedule': 300.0,  # Every 5 minutes
    },
    'send-budget-alerts': {
        'task': 'tracker.tasks.send_budget_alerts',
        'schedule': 3600.0,  # Every hour
    },
    'generate-weekly-reports': {
        'task': 'tracker.tasks.generate_weekly_reports',
        'schedule': 604800.0,  # Every week (Sunday at midnight)
    },
    'cleanup-old-attachments': {
        'task': 'tracker.tasks.cleanup_old_attachments',
        'schedule': 86400.0,  # Every day
    },
    'sync-recurring-transactions': {
        'task': 'tracker.tasks.sync_recurring_transactions',
        'schedule': 86400.0,  # Every day
    },
}

# Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    broker_connection_retry_on_startup=True,
)

@app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery setup"""
    print(f'Request: {self.request!r}')
    return 'Celery is working!'
