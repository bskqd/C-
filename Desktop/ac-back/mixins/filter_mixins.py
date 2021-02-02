import re
from itertools import chain

from django.db.models import Q
from django.utils import timezone as tz

from communication.models import SailorKeys
from sailor.models import Profile


class SailorFilter:
    @staticmethod
    def __get_field_lookup(lookup_value, lookup_mapping_tuple=None, default_lookup='__icontains'):
        if not lookup_mapping_tuple:
            lookup_mapping_tuple = (
                (r'^\*([\d\w]*)$', '__iendswith'),
                (r'^([\d\w]*)\*$', '__istartswith'),
                (r'^\*([\d\w]*)\*$', '__icontains')
            )
        for lookup_mapping in lookup_mapping_tuple:
            res = re.search(lookup_mapping[0], lookup_value)
            if res:
                return lookup_mapping[1], res.group(1).replace('*', '')
        return default_lookup, lookup_value.replace('*', '')

    def get_sailor_id(self, value, field_name):
        lookup = self.__get_field_lookup(value, default_lookup='')
        # print(lookup)
        sk = SailorKeys.objects.filter(**{
            'id{}'.format(lookup[0]): lookup[1],
            '{}__isnull'.format(field_name): False
        }).values_list(field_name, flat=True)
        # print(sk)
        return tuple(chain.from_iterable(sk))

    def get_sailor_name(self, value, field_name):
        lookup = self.__get_field_lookup(value)
        filtering = None
        names = value.split(' ')
        if len(names) == 1:
            lookup = self.__get_field_lookup(names[0])
            filtering = Q(
                **{'first_name_ukr{}'.format(lookup[0]): lookup[1]}
            ) | Q(
                **{'last_name_ukr{}'.format(lookup[0]): lookup[1]}
            ) | Q(
                **{'first_name_eng{}'.format(lookup[0]): lookup[1]}
            ) | Q(
                **{'last_name_eng{}'.format(lookup[0]): lookup[1]}
            )
        elif len(names) == 2:
            lookup0 = self.__get_field_lookup(names[0])
            lookup1 = self.__get_field_lookup(names[1])
            filtering = Q(
                **{'first_name_ukr{}'.format(lookup0[0]): lookup0[1]}
            ) & Q(
                **{'last_name_ukr{}'.format(lookup1[0]): lookup1[1]}
            ) | Q(
                **{'first_name_ukr{}'.format(lookup1[0]): lookup1[1]}
            ) & Q(
                **{'last_name_ukr{}'.format(lookup0[0]): lookup0[1]}
            ) | Q(
                **{'first_name_eng{}'.format(lookup0[0]): lookup0[1]}
            ) & Q(
                **{'last_name_eng{}'.format(lookup1[0]): lookup1[1]}
            ) | Q(
                **{'first_name_eng{}'.format(lookup1[0]): lookup1[1]}
            ) & Q(
                **{'last_name_eng{}'.format(lookup0[0]): lookup0[1]}
            )
        elif len(names) == 3:
            lookup0 = self.__get_field_lookup(names[0])
            lookup1 = self.__get_field_lookup(names[1])
            lookup2 = self.__get_field_lookup(names[2])
            filtering = Q(
                **{'first_name_ukr{}'.format(lookup0[0]): lookup0[1]}
            ) & Q(
                **{'middle_name_ukr{}'.format(lookup1[0]): lookup1[1]}
            ) & Q(
                **{'last_name_ukr{}'.format(lookup2[0]): lookup2[1]}
            ) | Q(
                **{'last_name_ukr{}'.format(lookup0[0]): lookup0[1]}
            ) & Q(
                **{'first_name_ukr{}'.format(lookup1[0]): lookup1[1]}
            ) & Q(
                **{'middle_name_ukr{}'.format(lookup2[0]): lookup2[1]}
            )

        profiles = Profile.objects.filter(filtering).values_list('id', flat=True)
        sk = SailorKeys.objects.filter(
            profile__in=list(profiles),
            **{'{}__isnull'.format(field_name): False}
        ).values_list(field_name, flat=True)
        return tuple(chain.from_iterable(sk))

    def get_sailor_birth(self, value, field_name):
        formats = {1: '%Y', 2: '%m.%Y', 3: '%d.%m.%Y', 4: '%Y-%m-%d'}
        if '-' in value:
            value_len = 4
        else:
            value_len = len(value.split('.'))

        birth_date = tz.datetime.strptime(value, formats[value_len])
        if value_len in [3, 4]:
            filtering = Q(date_birth=birth_date)
        elif value_len == 2:
            filtering = Q(date_birth__year=birth_date.year) & Q(date_birth__month=birth_date.month)
        elif value_len == 1:
            filtering = Q(date_birth__year=birth_date.year)
        profiles = list(Profile.objects.filter(filtering).values_list('id', flat=True))
        sk = SailorKeys.objects.filter(
            profile__in=profiles,
            **{'{}__isnull'.format(field_name): False}
        ).values_list(field_name, flat=True)
        return tuple(chain.from_iterable(sk))
