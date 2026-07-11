import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_cobranza.settings')

app = Celery('proyecto_cobranza')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-batch-completion-every-5-min': {
        'task': 'apps.calls.tasks.check_batch_completion',
        'schedule': crontab(minute='*/5'),
    },
}
