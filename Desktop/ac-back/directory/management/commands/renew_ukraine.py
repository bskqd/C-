import json
import re

from django.core.management import BaseCommand
from translitua import translit

from directory.models import City, Country, Region

settlements_type = {'М': 0, 'С': 4, 'Щ': 3, 'Т': 1}


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.states = {}
        self._substates = {}
        self.settlements = {}

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input', dest='fname', default='./koatuu.json', type=str)
        parser.add_argument('-c', '--country', dest='country', default='Ukraine', type=str)

    def handle(self, *args, **options):
        dnp = {}
        try:
            with open(options.get('fname'), 'r') as jf:
                dnp = json.load(jf)
            if dnp and dnp.get('level1'):
                country = Country.objects.get(value_eng=options.get('country'))
                if not country or not country.id:
                    raise Exception('There is no {} in database'.format(options.get("country")))
                regions = Region.objects.filter(country_id=country.id)
                regions_ids = regions.values_list('id', flat=True)
                regs = dnp.get('level1')
                self._get_struct(regs)

                regions.delete()
                # Create states

                for state in self.states:
                    state_name = self.states[state].capitalize()
                    region = Region(
                        country_id=country.id,
                        value=state_name,
                        value_eng=translit(state_name)
                    )
                    region.save()
                    try:
                        City.objects.bulk_create(
                            [City(
                                region_id=region.id,
                                value=c[0],
                                value_eng=translit(c[0]),
                                city_type=c[1]
                            ) for c in self.settlements[state]]
                        )
                    except Exception as e:
                        self.stdout.write('Something went wrong: {}'.format(e))
                        self.stdout.write(self.settlements)
        except Exception as e:
            self.stdout.write('Something went wrong {}:'.format(e))

    def _get_struct(self, regs):
        """

        :param regs: list of regions
        :param level: depth of region statements to parse
        :return:

        region code - string of digits 'aabccdeeff', where
            aa - code of state
            b - type of statement:
                1 - cities and towns
                2 - districts of state
                3 - districts of city
            cc - number of statement (city or district) (if b=1, cc=01 - state main city)
            d - territorial unit type
            ee - territorial unit number
            ff - territorial subunit number
        """
        for reg in regs:
            code = re.search(r'^(\d{2})(\d{1})(\d{2})(\d{1})(\d{2})\d{2}', reg.get('code')).groups()
            if not int(code[1]):
                try:
                    name = re.search(r'^([\w\-\t ]*)[/М\.](\w+)', reg.get('name')).groups()
                    if len(name[0]) > 1:
                        name = name[0].capitalize()
                    else:
                        name = name[1].capitalize()
                        if code[0] not in self.settlements:
                            self.settlements[code[0]] = []
                        self.settlements[code[0]].append((
                            name,
                            0,
                            reg.get('code')
                        ))
                except Exception as e:
                    pass
                self.states.update({code[0]: name})
                self._substates.update({code[0]: name})

            if reg.get('level2'):
                regs2 = reg.get('level2')
                for reg2 in regs2:
                    code = re.search(r'^(\d{2})(\d{1})(\d{2})(\d{1})(\d{2})\d{2}', reg2.get('code')).groups()
                    if code[1] in ('1', '2', '3'):
                        name = reg2.get('name')

                        if not int(code[2]):
                            continue
                        if code[1] == '2':
                            try:
                                name = re.search(r'^([\w\-\t`\' ]*)/(\w+)', name).group(1).capitalize()
                            except Exception as e:
                                self.stdout(e)
                            self._substates.update(
                                {
                                    reg2.get('code')[:5]: '({})'.format(name)
                                })
                        elif code[1] == '1':
                            if not int(code[2]):
                                continue
                            else:
                                if code[0] not in self.settlements:
                                    self.settlements[code[0]] = []
                                self._substates.update(
                                    {
                                        reg2.get('code')[:5]: '({})'.format(name.capitalize())
                                    })
                                self.settlements[code[0]].append((
                                    reg2.get('name').capitalize(),
                                    0,
                                    reg2.get('code')[:2]
                                ))
                    if reg2.get('level3'):
                        self._get_settlements(reg2.get('level3'))

    def _get_settlements(self, regs):
        for reg in regs:
            s_type = reg.get('type')
            if s_type in ('М', 'С', 'Щ', 'Т'):
                code = reg.get('code')[:2]
                if code not in self.settlements:
                    self.settlements[code] = []
                region_name = self._substates.get(reg.get("code")[:5])
                if not region_name or region_name == 'None':
                    region_name = '({})'.format(self._substates.get(reg.get("code")[:2]))
                self.settlements[code].append((
                    '{} {}'.format(reg.get("name").capitalize(), region_name),
                    settlements_type.get(s_type, 0),
                    reg.get('code')
                ))
            if reg.get('level4'):
                self._get_settlements(reg.get('level4'))
