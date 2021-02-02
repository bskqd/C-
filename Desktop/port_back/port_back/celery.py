import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'port_back.settings')

celery_app = Celery('port_back')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
   from notifications.tasks import (clear_user_notifications)
   sender.add_periodic_task(
      crontab(hour=0, minute=0), clear_user_notifications.s(),
   )
