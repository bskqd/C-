from datetime import timedelta

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from itcs import magic_numbers

User = get_user_model()


def create_JWT(user_id=magic_numbers.celery_user_id):
    celery_user = User.objects.get(id=user_id)
    refresh = RefreshToken.for_user(celery_user)
    access = refresh.access_token
    access.set_exp(lifetime=timedelta(hours=1))
    return access
