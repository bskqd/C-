from datetime import date, datetime

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework.authtoken.models import Token

import training.utils
from itcs import magic_numbers, celery_app
from sms_auth.models import HistoryNotification
from training.models import AvailableExamsToday

User = get_user_model()


@celery_app.task
def update_token_user(domain=None):
    try:
        user = User.objects.get(id=magic_numbers.AST_USER_ID)
    except User.DoesNotExist:
        raise ValidationError('User not found')
    try:
        token = Token.objects.get(user=user)
        if token.created.date() != date.today():
            token.delete()
            raise Token.DoesNotExist()
    except Token.DoesNotExist:
        token = Token.objects.create(user=user)
    url = (domain or settings.AST_URL) + '/administration/ac_token/'
    requests.post(url, json={'key': token.key})


@celery_app.task
def update_available_exams(domain=None):
    AvailableExamsToday.objects.all().delete()
    token = training.utils.create_JWT()
    url = (domain or settings.AST_URL) + '/examination/list_exams_today/'
    req = requests.get(url, headers={'Authorization': f'Token {token}'})
    if req.status_code not in (200, 201):
        send_warning_AST_mail.s(req.status_code).apply_async()
        raise ValidationError('Can not get good answer from AST', code=500)
    resp_json = req.json()
    exams = []
    for response in resp_json:
        list_positions = []
        for position in response['positions']:
            list_positions.append(position['id'])
        datetime_meeting = datetime.strptime(response['datetime_meeting'], '%H:%M:%S %d.%m.%Y')
        datetime_end_meeting = datetime.strptime(response['datetime_end_meeting'], '%H:%M:%S %d.%m.%Y')
        exams.append(AvailableExamsToday(list_positions=sorted(list_positions),
                                         datetime_meeting=datetime_meeting,
                                         datetime_end_meeting=datetime_end_meeting))
    AvailableExamsToday.objects.bulk_create(exams)
    return True


@celery_app.task
def send_warning_AST_mail(status_code):
    today = datetime.today().strftime('%d.%m.%Y')
    recipients = ['i.golubev@disoft.us', 'r.evdokimov@disoft.us']
    subject = '[AST] ERROR while getting exams'
    text_message = f'The list of exams available today {today} was not received. Error status - {status_code}'
    mail_resp = send_mail(subject, text_message, 'help@itcs.net.ua', recipients)
    for recipient in recipients:
        HistoryNotification.objects.create(destination=recipient, message=text_message,
                                           status_answer=mail_resp, date_answer=timezone.now(),
                                           type='Mail')
    return True
