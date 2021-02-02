from datetime import datetime, timedelta, timezone

from rest_framework.exceptions import ValidationError

from communication.models import SailorKeys
from itcs import magic_numbers
from itcs.celery import celery_app
from sailor.models import Profile
from .misc import create_user_for_personal_cabinet
from .models import SecurityCode, UserStatementVerification


@celery_app.task
def clear_sms_security_code():
    minuts_ago = datetime.now(timezone.utc) - timedelta(minutes=30)
    SecurityCode.objects.filter(created_at__lt=minuts_ago).delete()
    return True


@celery_app.task
def check_and_register_sailor(statement_id):
    """
    Checks the existence of a sailor in the AS by last_name_ukr, first_name_ukr, middle_name_ukr and date of birth.
    If only one sailor is found, will link the sailor in AS to the sailor's personal cabinet.
    """
    statement = UserStatementVerification.objects.get(id=statement_id)
    profile = Profile.objects.filter(
        last_name_ukr__iexact=statement.last_name,
        first_name_ukr__iexact=statement.first_name,
        middle_name_ukr__iexact=statement.middle_name
    ).filter(date_birth=statement.birthday)

    if profile.count() == 1:
        try:
            sailor_key = SailorKeys.objects.get(profile=profile.first().pk, user_id__isnull=True)
        except (SailorKeys.DoesNotExist, SailorKeys.MultipleObjectsReturned):
            return False
        if not statement.sailor_id and statement.status_document.id == magic_numbers.VERIFICATION_STATUS:
            statement.sailor_id = sailor_key.pk
            statement.status_document_id = magic_numbers.status_statement_to_per_cabinet_approv
            statement.save(update_fields=['sailor_id', 'status_document'])
            try:
                create_user_for_personal_cabinet(statement=statement)
            except ValidationError:
                return False
        return True
    return False
