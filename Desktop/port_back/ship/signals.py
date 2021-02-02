from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

import ship.models
from port_back.middleware import (get_current_authenticated_user)
from ship.tasks import save_history


@receiver(post_save, sender=ship.models.ShipInPort)
@receiver(post_save, sender=ship.models.ShipAgentNomination)
@receiver(post_save, sender=ship.models.IORequest)
@receiver(post_save, sender=ship.models.MainInfo)
@receiver(post_save, sender=ship.models.ShipStaff)
def save_history_signal(sender, instance, created, *args, **kwargs):
    history_type = ship.models.ShipHistory.CREATE if created else ship.models.ShipHistory.EDIT
    user = get_current_authenticated_user()
    user_id = user.pk if user else None
    save_history.s(instance, history_type, user_id=user_id).apply_async(countdown=3)


@receiver(post_delete, sender=ship.models.ShipInPort)
@receiver(post_delete, sender=ship.models.ShipAgentNomination)
@receiver(post_delete, sender=ship.models.IORequest)
@receiver(post_delete, sender=ship.models.MainInfo)
@receiver(post_delete, sender=ship.models.ShipStaff)
def delete_history_signal(sender, instance, *args, **kwargs):
    history_type = ship.models.ShipHistory.DELETE
    user = get_current_authenticated_user()
    user_id = user.pk if user else None
    save_history.s(instance, history_type, user_id=user_id).apply_async(countdown=3)
