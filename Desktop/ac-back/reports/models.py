from uuid import uuid5, NAMESPACE_DNS

from django.conf import settings
from django.db import models

# Create your models here.


class ProtocolFiles(models.Model):
    file_path = models.FilePathField(max_length=300)
    token = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.token = uuid5(NAMESPACE_DNS, self.file_path)
        super().save(*args, **kwargs)
        return self

    @property
    def file_name(self):
        return self.file_path.split('/')[-1]