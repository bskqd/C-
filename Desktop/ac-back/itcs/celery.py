import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itcs.settings')

celery_app = Celery('itcs')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    from agent.tasks import (informing_agent_sailor_about_expiration_proxy, delete_relationship_agent_sailor,
                             clear_security_code_to_statement_agent_sailor)
    from sailor.tasks import (clear_unsuccess_dkk, clear_unsuccess_qualification, change_status_certificate_qual,
                              change_status_medical_certificate, change_status_ntz_to_expired,
                              change_status_proof_diploma_to_expired,
                              change_status_sailor_passport, clear_unsuccess_demand, change_status_protocol_dkk,
                              check_to_resend_sms_additional_verification)
    from sms_auth.tasks import clear_sms_security_code
    from delivery.tasks import (check_nova_poshta_city, check_nova_poshta_warehouse)
    from training.tasks import update_token_user
    from cadets.tasks import clear_students_id
    from back_office.tasks import update_ntz_month_amount, check_payed_packet_item
    from notifications.tasks import (check_unpaid_statement_dkk, check_unpaid_statement_service_record,
                                     check_unpaid_statement_qual_doc)
    from training.tasks import (update_available_exams, )
    from certificates.tasks import delete_month_ratio_on_end_course
    sender.add_periodic_task(
        crontab(minute='*/30'), clear_unsuccess_dkk.s(),
    ),
    sender.add_periodic_task(
        crontab(minute='*/30'), clear_unsuccess_qualification.s(),
    ),
    # sender.add_periodic_task(
    #     crontab(hour='*/5', minute=0)
    # ),
    sender.add_periodic_task(
        crontab(hour=0, minute=0), change_status_ntz_to_expired.s(),
    ),
    sender.add_periodic_task(
        crontab(hour=0, minute=10), change_status_certificate_qual.s(),
    ),
    sender.add_periodic_task(
        crontab(hour=0, minute=20), change_status_proof_diploma_to_expired.s()
    ),
    sender.add_periodic_task(
        crontab(hour=0, minute=30), change_status_medical_certificate.s()
    ),
    sender.add_periodic_task(
        crontab(hour=0, minute=40), clear_unsuccess_demand.s()
    ),
    sender.add_periodic_task(
        crontab(hour=0, minute=50), change_status_protocol_dkk.s()
    ),
    sender.add_periodic_task(
        crontab(hour=1, minute=0), check_nova_poshta_city.s()
    ),
    sender.add_periodic_task(
        crontab(hour=1, minute=10), check_nova_poshta_warehouse.s()
    ),
    sender.add_periodic_task(
        crontab(day_of_week='sun', hour=1, minute=0), check_nova_poshta_warehouse.s()
    ),
    sender.add_periodic_task(
        crontab(day_of_week='sun', hour=1, minute=10), clear_students_id.s()
    ),
    sender.add_periodic_task(
        crontab(hour='*/5', minute=0), change_status_sailor_passport.s()
    ),
    sender.add_periodic_task(
        crontab(hour='*/5', minute=0), clear_sms_security_code.s()
    ),
    sender.add_periodic_task(
        crontab(hour=0, minute=0), update_token_user.s()
    )
    sender.add_periodic_task(
        crontab(day_of_month=1, hour=0, minute=1), update_ntz_month_amount.s()
    )
    sender.add_periodic_task(
        crontab(minute='*/30'), check_unpaid_statement_dkk.s()
    )
    sender.add_periodic_task(
        crontab(minute='*/30'), check_unpaid_statement_service_record.s()
    )
    sender.add_periodic_task(
        crontab(minute='*/30'), check_unpaid_statement_qual_doc.s()
    )
    sender.add_periodic_task(
        crontab(hour='*/1'), check_payed_packet_item.s(),
    )
    sender.add_periodic_task(
        crontab(hour=0, minute=0), delete_relationship_agent_sailor.s(),
    )
    sender.add_periodic_task(
        crontab(hour=8, minute=0), informing_agent_sailor_about_expiration_proxy.s(),
    )
    sender.add_periodic_task(
        crontab(hour='*/1'), clear_security_code_to_statement_agent_sailor.s(),
    )
    sender.add_periodic_task(
        crontab(hour=2, minute=0), update_available_exams.s(),
    )
    sender.add_periodic_task(
        crontab(hour=1, minute=0), delete_month_ratio_on_end_course.s()
    )
    if settings.ENABLE_ADDITIONAL_VERIFICATION is True:
        sender.add_periodic_task(
            crontab(minute='*/30'), check_to_resend_sms_additional_verification.s()
        )
