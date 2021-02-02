from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from sailor.models import Profile
from communication.models import SailorKeys
# Create your models here.


class DocumentsToVerification(models.Model):
    sailor_key = models.PositiveIntegerField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    datetime_add = models.DateTimeField(auto_now_add=True)
    type_document = models.CharField(max_length=150)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ('sailor_key', 'content_type', 'object_id')
    
    @property
    def get_profile_id_by_key(self):
        sailor_key = SailorKeys.objects.filter(id=self.sailor_key).first()
        return sailor_key.profile
    
    def save(self, *args, **kwargs):
        if not self.profile_id or not self.profile:
            self.profile_id = self.get_profile_id_by_key
        return super(DocumentsToVerification, self).save(*args, **kwargs)