from datetime import timedelta

from django.conf import settings
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.utils import timezone
from itcs import magic_numbers


def expires_in(token):
    time_elapsed = timezone.now() - token.created
    left_time = timedelta(minutes=settings.TIME_SESSION) - time_elapsed
    return left_time


# token checker if token expired or not
def is_token_expired(token):
    return expires_in(token) < timedelta(seconds=0)


def token_expire_handler(token):
    is_expired = is_token_expired(token)
    if is_expired and (token.user_id not in [magic_numbers.ntz_user_id, magic_numbers.AST_USER_ID] and
        not str(token.user.username).startswith(('key_', '+380', 'eti.online'))):
        token.delete()
        token, _ = Token.objects.update_or_create(user=token.user)
    return is_expired, token


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted')

        # This is required for the time comparison

        is_expired, token = token_expire_handler(token)
        if is_expired and (token.user_id not in [magic_numbers.ntz_user_id, magic_numbers.AST_USER_ID] and
                           not str(token.user.username).startswith(('key_', '+380', 'eti.online'))):
            raise exceptions.AuthenticationFailed('Token has expired')

        return token.user, token
