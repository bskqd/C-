from django.conf import settings
from django.utils import timezone

import notifications.tasks
from authorization.mail.models import UserInvitation
from port_back.celery import celery_app


@celery_app.task
def send_mail_to_agent(inv_agent_key):
    user_inv = UserInvitation.objects.get(key=inv_agent_key)
    title = 'Service invitation'
    data_for_template = {
        'name': user_inv.inviter.get_user_full_name,
        'url_activate': f'{settings.HOST_DOMAIN}/registration_agent/{user_inv.key}/',
    }
    notifications.tasks.send_email(
        email=user_inv.email,
        title=title,
        template_name='invite.html',
        data_for_template=data_for_template,
    )
    user_inv.sent = timezone.now()
    user_inv.save(update_fields=['sent'])
    return True


@celery_app.task
def send_registration_mail(email, password):
    title = 'The invitation to port control'
    data_for_template = {
        'username': email,
        'password': password,
        'url': settings.HOST_DOMAIN
    }
    notifications.tasks.send_email(
        email=email,
        title=title,
        template_name='registration.html',
        data_for_template=data_for_template,
    )
    return True
