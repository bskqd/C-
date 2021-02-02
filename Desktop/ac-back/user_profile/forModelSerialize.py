from sailor.AbstractSerializer import ModifiedRelatedField


class UserProfileSerializator(ModifiedRelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        response = {'branch_office': {'id': qs.branch_office_id, 'name_ukr': qs.branch_office.name_ukr,
                                      'name_eng': qs.branch_office.name_eng}, 'middle_name': qs.middle_name,
                    'city': {'id': qs.city.id, 'name': qs.city.value,
                             'region': {'id': qs.city.region.id, 'value': qs.city.region.value,
                                        'country': {'id': qs.city.region.country.id,
                                                    'value': qs.city.region.country.value,
                                                    'value_eng': qs.city.region.country.value_eng}}},
                    'additional_data': qs.additional_data, 'language': qs.language,
                    'is_commissioner': qs.is_commissioner, 'type_user': qs.type_user,
                    'is_trained': qs.is_trained}
        return response
