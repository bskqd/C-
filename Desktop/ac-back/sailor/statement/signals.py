import logging
import os

import logstash
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from certificates.tasks import delete_statement_to_eti
from sailor.statement.models import StatementSQC, StatementETI
from sailor.statement.tasks import sync_statement_sqc


@receiver(post_save, sender=StatementSQC)
def sync_sqc_statement(sender, instance, *args, **kwargs):
    sync_statement_sqc.s(instance.pk).apply_async(countdown=20)


@receiver(post_delete, sender=StatementETI)
def eti_integration_delete(sender, instance, **kwargs):
    print('signal eti delete')
    delete_statement_to_eti.s(instance.pk).apply_async()


def initialize_logstash(logger=None, loglevel=logging.INFO, **kwargs):
    handler = logstash.TCPLogstashHandler('10.64.10.72', 5000, tags=['celery'],
                                          message_type=f'AC-ITCS-{os.getenv("PROJECT_ENV", "localhost")}', version=1)
    handler.setLevel(loglevel)
    logger.addHandler(handler)
    return logger


from celery.signals import after_setup_task_logger

after_setup_task_logger.connect(initialize_logstash)
from celery.signals import after_setup_logger

after_setup_logger.connect(initialize_logstash)
