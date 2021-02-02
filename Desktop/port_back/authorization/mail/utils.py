from rest_framework.exceptions import ValidationError

import authorization.mail.tasks
from authorization.mail.models import UserInvitation
from core.models import User
from directory.models import Agency


def create_invite_for_agent(inviter: User, email: str, agency: Agency):
    """
    Сreates an invitation to the agent and send him an email
    """
    if User.objects.filter(email=email).exists():
        raise ValidationError('User with this email already exists')
    if UserInvitation.objects.filter(email=email).exists():
        raise ValidationError('This email is used')
    invite = UserInvitation.objects.create(inviter=inviter, email=email, agency=agency)
    authorization.mail.tasks.send_mail_to_agent.s(invite.pk).apply_async()
    return invite
