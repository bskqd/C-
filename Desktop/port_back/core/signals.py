from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

import core.models
from core.tasks import save_user_history
from port_back.middleware import (get_current_authenticated_user)


@receiver(post_save, sender=core.models.UserMarad)
@receiver(post_save, sender=core.models.HarborMaster)
@receiver(post_save, sender=core.models.HeadAgency)
@receiver(post_save, sender=core.models.Agent)
@receiver(post_save, sender=core.models.HarborWorker)
@receiver(post_save, sender=core.models.User)
def save_history_signal(sender, instance, created, *args, **kwargs):
    history_type = core.models.UserHistory.CREATE if created else core.models.UserHistory.EDIT
    user = get_current_authenticated_user()
    user_id = user.pk if user else None
    save_user_history.s(instance, history_type, author_id=user_id).apply_async(countdown=3)


@receiver(post_delete, sender=core.models.UserMarad)
@receiver(post_delete, sender=core.models.HarborMaster)
@receiver(post_delete, sender=core.models.HeadAgency)
@receiver(post_delete, sender=core.models.Agent)
@receiver(post_delete, sender=core.models.HarborWorker)
@receiver(post_delete, sender=core.models.User)
def delete_history_signal(sender, instance, *args, **kwargs):
    history_type = core.models.UserHistory.DELETE
    user = get_current_authenticated_user()
    user_id = user.pk if user else None
    save_user_history.s(instance, history_type, author_id=user_id).apply_async(countdown=3)
