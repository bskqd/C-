from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management import BaseCommand

from directory.models import BranchOffice, Country, Region, City
from user_profile.models import UserProfile, MainGroups

User = get_user_model()


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-u', '--username', dest='username', default=None, type=str)
        parser.add_argument('-m', '--middlename', dest='middle_name', default='', type=str)

    def handle(self, *args, **options):
        username = options['username']
        middle_name = options['middle_name']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise ValueError('User not found')
        branch_office, _ = BranchOffice.objects.get_or_create(code_branch='00', name_ukr='Стандартная филия',
                                                              name_eng='Default branch', house_num='00'
                                                              )
        country, _ = Country.objects.get_or_create(value='Стандартная страна', value_abbr='DCO',
                                                   value_eng='Default country')
        region, _ = Region.objects.get_or_create(value='Стандартный регион', value_eng='Default region',
                                                 country=country)
        city, _ = City.objects.get_or_create(value='Стандартный город', value_eng='Default city', region=region)
        group, _ = Group.objects.get_or_create(name='Default group')
        group.permissions.set(Permission.objects.all())
        main_group, _ = MainGroups.objects.get_or_create(name='Default Group')
        main_group.group.add(group)
        profile = UserProfile.objects.create(user=user, branch_office=branch_office, middle_name=middle_name, city=city)
        profile.main_group.add(main_group)
        return 'User profile for user "{}" was created'.format(username)
