import Levenshtein as lv

from itertools import combinations, starmap

from django.core.management import BaseCommand
from django.db.models import Count, ObjectDoesNotExist
from django.utils import timezone as tz
from django.conf import settings

from communication.models import SailorKeys, SailorKeysRefactor
from sailor.models import Profile


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.mappings = []
        self.to_delete = []
        self.count = 0

    def add_arguments(self, parser):
        parser.add_argument(
            '-d',
            '--start_date',
            help='Search from date',
            dest='start_date',
            default=None,
            type=str
        )

        parser.add_argument(
            '-s',
            '--search_date',
            help='Search for date',
            dest='search_date',
            default=None,
            type=str
        )

        parser.add_argument(
            '-i',
            '--start_from_id',
            help='Search from id',
            dest='start_id',
            default='0',
            type=str
        )

    def handle(self, *args, **options):
        birth_dates = Profile.objects
        if options.get('search_date'):
            birth_dates = birth_dates.filter(date_birth=tz.datetime.strptime(options.get('search_date'), '%Y-%m-%d'))
        birth_dates = birth_dates.values('date_birth').annotate(
            num_users=Count('date_birth')
        ).filter(num_users__gte=2, id__gte=int(options.get('start_id', 1))).order_by('-num_users')
        print(options.get('search_date'))

        print('Birth_dates: {}'.format(len(birth_dates)))
        # print('Birth dates for users {}'.format(birth_dates))
        for bd in birth_dates:

            users = Profile.objects.filter(date_birth=bd.get('date_birth'), id__gte=int(options.get('start_id', 1)))
            print('Getting {} users for {} birth_date'.format(len(users), bd.get('date_birth')))

            if len(users) > 1:
                self.mappings.extend([comb[1] for comb in self._get_mappings(users, 2) if comb[0]])
                # print(self.mappings)
            self.count += 1
            print('Processed {} dates of {} ({}%). Find {} records for mapping'.format(
                self.count,
                len(birth_dates),
                round((self.count/len(birth_dates))*100, 2),
                len(self.mappings)
            ))
            self.to_delete = []
            for m in self.mappings:
                keys = self._sort_longest_record(m)
                if not keys:
                    continue
                old_key = SailorKeysRefactor(
                    profile=keys[1].profile,
                    profile_changed_to=keys[0].profile,
                    qualification_documents=keys[1].qualification_documents,
                    service_records=keys[1].service_records,
                    experience_docs=keys[1].experience_docs,
                    education=keys[1].education,
                    sertificate_ntz=keys[1].sertificate_ntz,
                    medical_sertificate=keys[1].medical_sertificate,
                    sailor_passport=keys[1].sailor_passport,
                    statement_dkk=keys[1].statement_dkk,
                    protocol_dkk=keys[1].protocol_dkk,
                    statement_qualification=keys[1].statement_qualification,
                    status=1,
                    status_description=1
                )
                try:
                    keys[0].qualification_documents = list(
                        set(
                            (keys[0].qualification_documents or []) + (keys[1].qualification_documents  or [])
                        )
                    )
                    keys[0].service_records = list(
                        set(
                            (keys[0].service_records or []) + (keys[1].service_records or [])
                        )
                    )
                    keys[0].experience_docs = list(
                        set(
                            (keys[0].experience_docs or []) + (keys[1].experience_docs or [])
                        )
                    )
                    keys[0].education = list(
                        set(
                            (keys[0].education or []) + (keys[1].education or [])
                        )
                    )
                    keys[0].sertificate_ntz = list(
                        set(
                            (keys[0].sertificate_ntz or []) + (keys[1].sertificate_ntz or [])
                        )
                    )
                    keys[0].medical_sertificate = list(
                        set(
                            (keys[0].medical_sertificate or []) + (keys[1].medical_sertificate or [])
                        )
                    )
                    keys[0].sailor_passport = list(
                        set(
                            (keys[0].sailor_passport or []) + (keys[1].sailor_passport or [])
                        )
                    )
                    keys[0].statement_dkk = list(
                        set(
                            (keys[0].statement_dkk or []) + (keys[1].statement_dkk or [])
                        )
                    )
                    keys[0].protocol_dkk = list(
                        set(
                            (keys[0].protocol_dkk or []) + (keys[1].protocol_dkk or [])
                        )
                    )
                    keys[0].statement_qualification = list(
                        set(
                            (keys[0].statement_qualification or []) + (keys[1].statement_qualification or [])
                        )
                    )
                    print('Record must be deleted {}'.format(keys[1].profile))
                    print('Updating record {}'.format(keys[0].profile))
                    keys[0].save()
                    # keys[1].delete()
                    self.to_delete.append(keys[1].profile)
                    old_key.status = 1
                    old_key.status_description = 1

                except Exception as e:
                    self.stdout.write('Something went wrong: {}'.format(e))
                    old_key.status = 2
                    old_key.status_description = 3
                finally:
                    old_key.save()
            self.mappings = []
            SailorKeys.objects.filter(profile__in=self.to_delete).delete()
            Profile.objects.filter(id__in=self.to_delete).delete()
            # self.to_delete = []
        print(len(self.mappings))

    def _sort_longest_record(self, mapping):
        mapping = list(mapping)
        if mapping[0] in self.to_delete:
            mapping[0] = SailorKeysRefactor.objects.filter(profile=mapping[0]).order_by('id').last().profile_changed_to
        if mapping[1] in self.to_delete:
            mapping[1] = SailorKeysRefactor.objects.filter(profile=mapping[1]).order_by('id').last().profile_changed_to

        try:
            key1 = SailorKeys.objects.get(profile=mapping[0])
            key2 = SailorKeys.objects.get(profile=mapping[1])
        except Exception as e:
            print(e)
            print(mapping)
            return tuple()

        field = 'sertificate_ntz'
        if len(getattr(key2, field, []) or []) > len(getattr(key1, field, []) or []):
            return key2, key1
        return key1, key2

    def _get_mappings(self, users, combination_len):
        return (m for m in starmap(self._get_distance, combinations(users, combination_len)))

    def _get_distance(self, source, target):
        if 0 < lv.distance(
                source.get_full_name_ukr,
                target.get_full_name_ukr
        ) <= settings.NAME_MAX_DISTANCE or 0 < lv.distance(
                source.get_full_name_eng,
                target.get_full_name_eng
        ) <= settings.NAME_MAX_DISTANCE:
            return True, (source.id, target.id)
        return False, ()
