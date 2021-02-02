from django.contrib.auth import get_user_model

from directory.models import Commisioner

User = get_user_model()

def delete_duplicates_commissioner():
    for commissioner in Commisioner.objects.all().reverse():
        if Commisioner.objects.filter(name=commissioner.name).count() > 1:
            commissioner.delete()


def get_or_create_commissioner(full_name: str, is_secretary=False):
    """
    :param: full_name - FIO of commissioner
    """
    full_name = full_name.strip()
    if not full_name:
        return None
    try:
        split_full_name = full_name.split()
        first_name = split_full_name[1]
        last_name = split_full_name[0]
        middle_name = split_full_name[2]
        try:
            user = User.objects.get(first_name__iexact=first_name, last_name__iexact=last_name,
                                    userprofile__middle_name__iexact=middle_name)
        except User.DoesNotExist:
            user = None
    except IndexError:
        user = None
    if user:
        commissioner, _ = Commisioner.objects.update_or_create(name=full_name, defaults={'user': user,
                                                                                         'is_disable': is_secretary})
    else:
        commissioner, _ = Commisioner.objects.get_or_create(name=full_name, defaults={'is_disable': is_secretary})
    return commissioner
