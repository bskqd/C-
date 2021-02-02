from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError

from agent.models import StatementAgentSailor, AgentSailor
from agent.tasks import send_agent_email, deactived_statement
from communication.models import SailorKeys
from sailor.models import ContactInfo
from sailor.tasks import save_history
from sms_auth.misc import generic_password
from user_profile.models import UserProfile, MainGroups
from user_profile.serializer import UserSerializer

User = get_user_model()


def create_user_agent(statement, create_user_id, group):
    """
    Создание пользователя (агента) из заявления агента
    """
    contact_info = list(statement.contact_info)
    email = ContactInfo.objects.filter(id__in=contact_info, type_contact_id=2).first()
    if not email:
        return 'Please enter your email address'
    username = email.value.split('@')[0]
    password = generic_password(8)
    try:
        user = User.objects.create_user(first_name=statement.first_name, last_name=statement.last_name,
                                        username=username,
                                        password=password)
    except IntegrityError:
        return 'Please use another email address'

    userprofile = UserProfile.objects.create(user_id=user.id, middle_name=statement.middle_name,
                                             contact_info=contact_info, type_user=UserProfile.AGENT,
                                             city_id=statement.city.id, branch_office_id=2)
    userprofile.agent_group.add(group)
    agent_group = MainGroups.objects.get(name='Довірена особа')
    userprofile.main_group.add(agent_group)
    all_group = Group.objects.filter(maingroups=agent_group)
    for item in all_group:
        user.groups.add(item)
    userprofile.save()
    save_history.s(user_id=create_user_id, module='UserProfile', action_type='create', content_obj=user,
                   serializer=UserSerializer, new_obj=user).apply_async(serializer='pickle')

    send_agent_email.s(email=email.value, password=password, username=username).apply_async()

    return True


def register_sailor_agent(sailor: SailorKeys, statement: StatementAgentSailor, user_change: User) -> None:
    """

    :param sailor: SailorKeys Instance
    :param statement: StatementAgentSailor instance
    :param user_change: User who do this change
    :return: boolean with statuses
    """
    from agent.serializers import AgentSailorSerializer
    if sailor.agent_id:
        raise ValidationError('Sailor has seaman')
    # td: datetime = datetime.now()
    # if AgentSailor.objects.filter(created_at__year=td.year, created_at__month=td.month, is_disable=False,
    #                               agent=statement.agent).count() >= 30:
    #     raise ValidationError('Agent has reached the limit for the current month')
    agent_sailor: AgentSailor = AgentSailor.objects.create(sailor_key=statement.sailor_key, agent=statement.agent,
                                                           date_end_proxy=statement.date_end_proxy)
    sailor.agent_id = agent_sailor.agent.id
    sailor.save(update_fields=['agent_id'])

    save_history.s(user_id=user_change.id, module='AgentSailor', action_type='create',
                   content_obj=agent_sailor, serializer=AgentSailorSerializer, new_obj=agent_sailor,
                   sailor_key_id=statement.sailor_key).apply_async(serializer='pickle')

    deactived_statement.s(sailor_key=statement.sailor_key,
                          user_id=user_change.id,
                          exclude_statement=statement.pk).apply_async()
