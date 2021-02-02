import requests

from itcs.celery import celery_app
from itcs.settings import API_KEY_NOVAPOSHTA, URL_API_NOVAPOSHTA
from delivery.models import (NovaPoshtaArea, NovaPoshtaCity, TypeDescription, NovaPoshtaWarehouse, NovaPoshtaStreet,
                             TypeStreet)


@celery_app.task(bind=True, max_retries=5)
def check_nova_poshta_city(self):
    added_obj = 0
    deleted_obj = 0
    request_json = {'apiKey': API_KEY_NOVAPOSHTA, 'modelName': 'Address', 'calledMethod': 'getCities',
                    'methodProperties': {}}
    response = requests.post(URL_API_NOVAPOSHTA, json=request_json)
    if response.status_code != 200:
        if self.request.retries < self.max_retries - 1:
            self.retry(countdown=60)
        else:
            return False
    data = response.json()['data']
    list_response = [city['Ref'] for city in data]
    list_have_city = NovaPoshtaCity.objects.all().values_list('ref', flat=True)
    not_cities = set(list_response) ^ set(list_have_city)
    if not not_cities:
        return 'added - {added}, deleted - {deleted} objects'.format(added=added_obj, deleted=deleted_obj)
    deleted_city = list(set(list_have_city) & not_cities)
    if deleted_city:
        deleted_obj = NovaPoshtaCity.objects.filter(ref__in=deleted_city).delete()[0]
    for city in data:
        if city['Ref'] not in not_cities:
            continue
        area_ref = city['Area']
        city_ref = city['Ref']
        ref_description = city['SettlementType']
        name_description = city.get('SettlementTypeDescription')
        if name_description is None:
            continue
        if NovaPoshtaCity.objects.filter(ref=city_ref).exists():
            continue
        try:
            type_description = TypeDescription.objects.get(ref_description_NP=ref_description)
        except TypeDescription.DoesNotExist:
            type_description = TypeDescription.objects.create(ref_description_NP=ref_description,
                                                              name_ukr=name_description)
        area = NovaPoshtaArea.objects.get(ref=area_ref)
        NovaPoshtaCity.objects.create(name_ukr=city['Description'], ref=city['Ref'], area_id=area.id,
                                      id_city=city['CityID'], type_description_id=type_description.id)
        added_obj += 1
    return 'added - {added}, deleted - {deleted} objects'.format(added=added_obj, deleted=deleted_obj)


@celery_app.task(bind=True, max_retries=5)
def check_nova_poshta_warehouse(self):
    added_obj = 0
    deleted_obj = 0
    request_json = {'apiKey': API_KEY_NOVAPOSHTA, 'modelName': 'AddressGeneral', 'calledMethod': 'getWarehouses',
                    'methodProperties': {}}
    response = requests.post(URL_API_NOVAPOSHTA, json=request_json)
    if response.status_code != 200:
        if self.request.retries < self.max_retries - 1:
            self.retry(countdown=60)
        else:
            return False
    data = response.json()['data']
    list_response = [warehouse['Ref'] for warehouse in data]
    list_have_warehouse = list(NovaPoshtaWarehouse.objects.all().values_list('ref', flat=True))
    not_warehouse = set(list_response) ^ set(list_have_warehouse)
    if not not_warehouse:
        return 'added - {added}, deleted - {deleted} objects'.format(added=added_obj, deleted=deleted_obj)
    deleted_warehouse = list(set(list_have_warehouse) & not_warehouse)
    if deleted_warehouse:
        deleted_obj = NovaPoshtaWarehouse.objects.filter(ref__in=deleted_warehouse).delete()[0]
    for warehouse in data:
        ref = warehouse['Ref']
        if ref not in not_warehouse:
            continue
        city_ref = warehouse['CityRef']
        try:
            city = NovaPoshtaCity.objects.get(ref=city_ref)
        except NovaPoshtaCity.DoesNotExist:
            continue
        NovaPoshtaWarehouse.objects.create(number=warehouse['Number'], code=warehouse['SiteKey'],
                                           name_ukr=warehouse['Description'], short_address=warehouse['ShortAddress'],
                                           ref=ref, city_id=city.id)
        added_obj += 1
    return 'added - {added}, deleted - {deleted} objects'.format(added=added_obj, deleted=deleted_obj)


@celery_app.task
def check_street_nova_poshta():
    page = 1
    type_street = TypeStreet.objects.all().values()
    _dict = dict()
    _type_street = [_dict.update({street['name_ukr']: street['id']}) for street in type_street]
    for city in NovaPoshtaCity.objects.all():
        while True:
            request_json = {'apiKey': API_KEY_NOVAPOSHTA, "modelName": "Address", "calledMethod": "getStreet",
                            "methodProperties": {"Page": page, "CityRef": city.ref}}
            response = requests.post(URL_API_NOVAPOSHTA, json=request_json)
            data_response = response.json()['data']
            if not data_response:
                page = 1
                break
            if len(data_response) == 500:
                page += 1
            else:
                page = 1
            streets = [NovaPoshtaStreet(ref=data['Ref'], name_ukr=data['Description'], city_id=city.pk,
                                        type_street_id=_dict[data['StreetsType']]) for data in data_response]
            NovaPoshtaStreet.objects.bulk_create(streets, ignore_conflicts=True)
            if page == 1:
                break
    return True