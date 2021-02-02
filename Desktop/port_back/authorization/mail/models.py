import binascii
import os

from django.db import models
from django.utils import timezone

from core.models import User, DateTimesABC


class UserInvitation(DateTimesABC):
    accepted = models.BooleanField(default=False)
    key = models.CharField(max_length=64, unique=True, blank=True, primary_key=True)
    sent = models.DateTimeField(null=True, blank=True)
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='inviter')
    email = models.EmailField(unique=True)
    created_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='created_user')
    agency = models.ForeignKey('directory.Agency', on_delete=models.PROTECT)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.key:
            self.key = binascii.hexlify(os.urandom(20)).decode()
        self.date_modified = timezone.now()
        return super().save(force_insert, force_update, using, update_fields)

    class Meta:
        permissions = (
            ('agent_admin_agency', 'Set agent as admin'),
        )
