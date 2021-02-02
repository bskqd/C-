import requests
from rest_framework.exceptions import ValidationError

from itcs.settings import API_KEY_NOVAPOSHTA, URL_API_NOVAPOSHTA
from delivery.models import (NovaPoshtaArea, NovaPoshtaCity, TypeDescription, NovaPoshtaWarehouse,NovaPoshtaStreet,
                             TypeStreet, NovaPoshtaDelivery)


def create_delivery_nova_poshta(data):
    is_courier = data['is_courier']
    street_id = data.get('street_id')
    other_street = data.get('other_street')
    city_id = data.get('city_id')
    warehouse_id = data.get('warehouse_id')
    house = data.get('house')
    if city_id is None:
        raise ValidationError('City is not defined')
    ids_warehouse = list(NovaPoshtaWarehouse.objects.filter(city__id=city_id).values_list('id', flat=True))
    if warehouse_id and warehouse_id not in ids_warehouse:
        raise ValidationError('Incorrect warehouse for this city')
    if warehouse_id is None and is_courier is False:
        raise ValidationError('Warehouse not defined')
    if warehouse_id:
        post = NovaPoshtaDelivery.objects.create(city_id=city_id, phone_number=data['phone_number'],
                                                 is_courier=is_courier, street=None, other_street=None, house=None,
                                                 apartment=None, warehouse_id=warehouse_id)
        return post.id
    if is_courier and street_id is None and other_street is None:
        raise ValidationError('Street is not defined')
    street = None
    if street_id:
        try:
            street = NovaPoshtaStreet.objects.get(id=street_id, city__id=city_id)
        except NovaPoshtaStreet.DoesNotExist:
            raise ValidationError('Street is not defined at city')
    if house is None:
        raise ValidationError('House is not defined')
    post = NovaPoshtaDelivery.objects.create(city_id=city_id, phone_number=data['phone_number'],
                                             is_courier=data['is_courier'], street=street, other_street=other_street,
                                             house=house, apartment=data.get('apartment'), warehouse_id=warehouse_id)
    return post.id
