from __future__ import division

import binascii
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class U2FKey(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='u2f_keys',
                             on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True)
    public_key = models.TextField(unique=True)
    key_handle = models.TextField()
    app_id = models.TextField()

    def to_json(self):
        return {
            'publicKey': self.public_key,
            'keyHandle': self.key_handle,
            'appId': self.app_id,
            'version': 'U2F_V2',
        }


class TmpToken(models.Model):
    key = models.CharField("Key", max_length=40, primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='tmp_token',
                                on_delete=models.CASCADE
                                )
    sign_req = models.JSONField(null=True, blank=True)
    created = models.DateTimeField("Created", auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @staticmethod
    def generate_key():
        return binascii.hexlify(os.urandom(20)).decode()


class AuthorizationLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                             related_name='ac_authorization_log')
    user_agent = models.TextField(default='')
    longitude = models.FloatField(null=True)
    latitude = models.FloatField(null=True)
    address = models.TextField(default='', null=True)
    ip_address = models.GenericIPAddressField()
    datetime_login = models.DateTimeField(auto_now_add=True)
