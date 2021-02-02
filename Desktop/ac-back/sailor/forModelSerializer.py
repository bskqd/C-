import json

from django.db.models import ObjectDoesNotExist
from rest_framework import serializers

from communication.models import SailorKeys
from directory.models import (BranchOffice, City, Country, Course, Decision,
                              DoctrorInMedicalInstitution, ExtentDiplomaUniversity, LevelQualification,
                              LimitationForMedical, Limitations, NTZ, NZ, Port, Position,
                              PositionForMedical, Rank, Responsibility, ResponsibilityWorkBook,
                              Sex, Speciality, Specialization, StatusDocument, TypeContact, TypeDocument,
                              TypeDocumentNZ)
from sailor.AbstractSerializer import ModifiedRelatedField
from sailor.document.models import ProtocolSQC
from sailor.models import (FullAddress, PhotoProfile, Profile)
# Main Info
from user_profile.models import UserProfile


class FullAddressSerializer(ModifiedRelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        return {'id': qs.id,
                'city': {'city': {'id': qs.city.id,
                                  'value': qs.city.value,
                                  'region': qs.city.region_id,
                                  'value_eng': qs.city.value_eng},
                         'region': {'country': qs.city.region.country.id,
                                    'id': qs.city.region_id,
                                    'value': qs.city.region.value,
                                    'value_eng': qs.city.region.value_eng},
                         'country': {'id': qs.city.region.country_id,
                                     'value': qs.city.region.country.value,
                                     'value_eng': qs.city.region.country.value_eng,
                                     'value_abbr': qs.city.region.country.value_abbr}
                         },
                'index': qs.index, 'street': qs.street, 'house': qs.house, 'flat': qs.flat}

    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError('empty data')
        if type(data) is not dict:
            raise serializers.ValidationError('Data error')
        else:
            try:
                data['city_id'] = data.pop('city')
            except KeyError:
                raise serializers.ValidationError('incorect dictinary')
            try:
                City.objects.get(id=data['city_id'])
            except ValueError:
                raise serializers.ValidationError('id must be a integer field')
            except City.DoesNotExist:
                raise serializers.ValidationError('City does not exists')
                # response.append(position)
        return FullAddress.objects.create(**data).id


class CitySerializator(ModifiedRelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            try:
                qs = self.queryset.get(id=obj)
            except ObjectDoesNotExist:
                return {'city': {'id': '', 'name': '', 'region_id': ''},
                        'region': {'id': '', 'name': '', 'country_id': ''},
                        'country': {'id': '', 'name': '',
                                    'name_eng': '',
                                    'value_abbr': ''}}
        else:
            qs = obj
        response = {'city': {'id': qs.id, 'name': qs.value, 'region': qs.region_id},
                    'region': {'id': qs.region.id, 'name': qs.region.value, 'country': qs.region.country_id,
                               'value_eng': qs.region.value_eng},
                    'country': {'id': qs.region.country.id, 'value': qs.region.country.value,
                                'value_eng': qs.region.country.value_eng,
                                'value_abbr': qs.region.country.value_abbr}}
        return response

    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError('empty data')
        if type(data) is not int:
            raise serializers.ValidationError('Data error')
        else:
            try:
                city = data
            #     region = data['region']
            #     country_ukr = data['country']['name']
            #     country_eng = data['country']['name_eng']
            #     value_abbr = data['country']['value_abbr']
            except KeyError:
                raise serializers.ValidationError('Incorect dictinary')
            try:
                return City.objects.get(id=city)
            except KeyError:
                raise serializers.ValidationError('id is requid field')
            except (ValueError, TypeError):
                raise serializers.ValidationError('id must be a integer field')
            except City.DoesNotExist:
                raise serializers.ValidationError('City does not exists')


class PassportSerializator(ModifiedRelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            try:
                qs = self.queryset.get(id=obj)
            except ObjectDoesNotExist:
                response = {'serial': '', 'date': '', 'issued_by': '', 'photo': '',
                            'country': {'id': '', 'value': '',
                                        'value_eng': '',
                                        'value_abbr': ''}}
                return response
        else:
            qs = obj
        try:
            photo_ids = json.loads(qs.photo)
            photo = list(PhotoProfile.objects.filter(id__in=photo_ids).values_list('photo', flat=True))
        except (json.decoder.JSONDecodeError, TypeError):
            photo = None
        response = {'serial': qs.serial, 'date': qs.date, 'issued_by': qs.issued_by, 'photo': photo,
                    'country': {'id': qs.country.id, 'value': qs.country.value, 'value_eng': qs.country.value_eng,
                                'value_abbr': qs.country.value_abbr}}
        return response

    def to_internal_value(self, data):
        from .models import Passport
        if not data:
            raise serializers.ValidationError('empty data')
        if type(data) is not dict:
            raise serializers.ValidationError('Data error')
        else:
            try:
                serial = data['serial']
            except KeyError:
                raise serializers.ValidationError('Incorect dictinary')
            # passport = object()
            try:
                user_id = data['user_id']
                user = SailorKeys.objects.get(id=user_id)
                profile = Profile.objects.get(id=user.profile)
                passport = Passport.objects.get(id=profile.passport)
            except (
                    KeyError, SailorKeys.DoesNotExist, Profile.DoesNotExist, Passport.DoesNotExist,
                    Country.DoesNotExist):
                user_id = None
                passport = None
            try:
                issued_by = data['issued_by']
            except KeyError:
                if passport:
                    issued_by = passport.issued_by
                else:
                    issued_by = ' '
            try:
                country = data['country']
                country = Country.objects.get(id=country)
            except (KeyError, Country.DoesNotExist):
                if passport:
                    country = passport.country
                else:
                    country = Country.objects.first()
            try:
                photo = data['photo']
            except KeyError:
                if passport:
                    photo = passport.photo
                else:
                    photo = None
            try:
                date_issued = data['date']
            except KeyError:
                if passport:
                    date_issued = passport.date
                else:
                    date_issued = None
            try:
                passport = Passport.objects.get(serial=serial, date=date_issued, issued_by=issued_by, country=country)
                return passport.id
            except KeyError:
                raise serializers.ValidationError('id is requid field')
            except (ValueError, TypeError):
                raise serializers.ValidationError('id must be a integer field')
            except Passport.DoesNotExist:
                passport = Passport.objects.create(serial=serial, date=date_issued, photo=photo, issued_by=issued_by,
                                                   country=country)
                return passport.id


class ContactSerializator(ModifiedRelatedField):
    def to_representation(self, obj):
        if not obj:
            return []
        try:
            obj = json.loads(obj)
        except TypeError:
            pass
        if type(obj) is list:
            qs = self.queryset.filter(id__in=obj)
        else:
            qs = obj
        response = [{'type_contact': val.type_contact.value, 'value': val.value} for val in qs]
        return response

    def to_internal_value(self, data):
        response = []
        from .models import ContactInfo
        if not data:
            return ContactInfo.objects.none()
            # raise serializers.ValidationError('empty data')
        if type(data) is not list:
            raise serializers.ValidationError('Data error')
        else:
            for val in data:
                try:
                    contact_type = val['type_contact']
                    value = val['value']
                except KeyError:
                    raise serializers.ValidationError('Incorect dictinary')
                contact_type, _ = TypeContact.objects.get_or_create(value=contact_type)
                try:
                    contact_info = ContactInfo.objects.filter(value=value, type_contact=contact_type).first()
                    if contact_info:
                        response.append(contact_info)
                    else:
                        contact = ContactInfo.objects.create(value=value, type_contact=contact_type)
                        response.append(contact)
                except KeyError:
                    pass
            return ContactInfo.objects.filter(id__in=[val.id for val in response])


class PositionSerializer(ModifiedRelatedField):
    def to_representation(self, obj):
        if not obj:
            return []
        if type(obj) is list:
            qs = self.queryset.filter(id__in=obj)
        else:
            qs = obj
        response = [{'id': val.id, 'name_ukr': val.name_ukr, 'name_eng': val.name_eng, 'rank': val.rank_id} for val in
                    qs]
        return response

    def to_internal_value(self, data):
        response = []
        if not data:
            raise serializers.ValidationError('empty data')
        if type(data) is not list:
            raise serializers.ValidationError('Type data incorect. Use list')
        else:
            for val in data:
                position_id = val
                try:
                    position = Position.objects.get(id=position_id)
                    response.append(position.id)
                except KeyError:
                    raise serializers.ValidationError('id is requid field')
                except ValueError:
                    raise serializers.ValidationError('id must be a integer field')
                except Position.DoesNotExist:
                    raise serializers.ValidationError('position {} does not exists'.format(position_id))
            return response


# class INNSerializator(ModifiedRelatedField):
#     def to_representation(self, obj):
#         if type(obj) is int:
#             try:
#                 qs = self.queryset.get(id=obj)
#             except ObjectDoesNotExist:
#                 return ''
#         else:
#             qs = obj
#         return qs.value
#
#     def to_internal_value(self, data):
#         if not data:
#             raise serializers.ValidationError('empty data')
#         else:
#             try:
#                 value = data
#             except KeyError:
#                 raise serializers.ValidationError('incorect dictinary')
#             try:
#                 inn = INN.objects.get(value=value)
#                 return inn.id
#             except KeyError:
#                 raise serializers.ValidationError('id is requid field')
#             except ValueError:
#                 raise serializers.ValidationError('id must be a integer field')
#             except INN.DoesNotExist:
#                 inn = INN.objects.create(value=value)
#                 return inn.id


class SexSerializator(ModifiedRelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        return {'id': qs.id, 'value_ukr': qs.value_ukr, 'value_eng': qs.value_eng}

    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError('empty data')
        else:
            try:
                id_sex = data
                sex = Sex.objects.get(id=id_sex)
                return sex
            except KeyError:
                raise serializers.ValidationError('id is requid field')
            except ValueError:
                raise serializers.ValidationError('id must be a integer field')
            except Sex.DoesNotExist:
                raise serializers.ValidationError('Sex does not exist')


class ResidentSerializer(ModifiedRelatedField):
    def to_representation(self, obj):
        null_resp = {'city': '', 'index_place': '', 'street': '', 'house': '', 'flat': ''}
        if not obj:
            return
        if type(obj) is int:
            try:
                qs = self.queryset.get(id=obj)
            except ObjectDoesNotExist:
                return null_resp
        else:
            qs = obj
        return {'city': {'city': {'id': qs.city.id, 'value': qs.city.value},
                         'region': {'id': qs.city.region.id, 'value': qs.city.region.value,
                                    'value_eng': qs.city.region.value_eng},
                         'county': {'id': qs.city.region.country.id, 'value': qs.city.region.country.value,
                                    'value_eng': qs.city.region.country.value_eng}},
                'index_place': qs.index, 'street': qs.street,
                'house': qs.house, 'flat': qs.flat}

    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError('empty data')
        else:
            city = data['city']
            index_place = data['index_place']
            street = data['street']
            house = data['house']
            try:
                flat = data['flat']
            except KeyError:
                flat = None
            return FullAddress.objects. \
                create(city_id=city, index=index_place, street=street, house=house, flat=flat).id


class PhotoSerializer(ModifiedRelatedField):
    def to_representation(self, obj):
        default_photo = [{'id': 0, 'photo': 'default_profile.png', 'is_delete': False}]
        request = self.context.get('request')
        user = request.user if hasattr(request, 'user') else None
        back_office = False
        if hasattr(user, 'userprofile'):
            back_office = user.userprofile.type_user == UserProfile.BACK_OFFICE
        if not obj or obj == '[]':
            return default_photo
        try:
            obj = json.loads(obj)
        except TypeError:
            pass
        if type(obj) is list:
            if user and (user.is_superuser or back_office):
                qs = list(self.queryset.filter(id__in=obj).values('id', 'photo', 'is_delete'))
            else:
                qs = list(self.queryset.filter(id__in=obj, is_delete=False).values('id', 'photo', 'is_delete'))
            if not qs:
                return default_photo
        else:
            try:
                qs = list(obj.values('id', 'photo', 'is_delete'))
            except Exception as e:  # TODO исправить это говно
                return default_photo
        return qs


class BranchOfficeSerializer(ModifiedRelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        return {'id': qs.pk, 'name_ukr': qs.name_ukr, 'name_eng': qs.name_eng}

    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError('empty data')
        else:
            try:
                id_branch_office = data
                branch_office = BranchOffice.objects.get(id=id_branch_office)
                return branch_office
            except KeyError:
                raise serializers.ValidationError('id is requid field')
            except ValueError:
                raise serializers.ValidationError('id must be a integer field')
            except BranchOffice.DoesNotExist:
                raise serializers.ValidationError('BranchOffice does not exist')


class RankSerializer(ModifiedRelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        return {'id': qs.id, 'name_ukr': qs.name_ukr, 'name_eng': qs.name_eng}

    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError('empty data')
        else:
            try:
                rank_id = data
            except KeyError:
                raise serializers.ValidationError('id is requid field')
            if type(rank_id) is not int:
                raise serializers.ValidationError('id must be a integer field')
            try:
                rank = Rank.objects.get(id=rank_id)
                return rank
            except Rank.DoesNotExist:
                raise serializers.ValidationError('Rank does not exists')


class ResponsibilitySerializer(ModifiedRelatedField):
    def to_representation(self, obj):
        if type(obj) is list:
            qs = self.queryset.filter(id__in=obj)
        else:
            qs = obj
        response = [{'name_ukr': val.name_ukr, 'name_eng': val.name_eng, 'id': val.id} for val in qs]
        return response

    def to_internal_value(self, data):
        if not data:
            return None
        else:
            function_id = data
            if type(function_id) is not list:
                raise serializers.ValidationError('Function must be a list field')
            try:
                func = list(Responsibility.objects.filter(id__in=function_id).values_list('id', flat=True))
                return func
            except Responsibility.DoesNotExist:
                raise serializers.ValidationError('Function does not exists')


# value in service record end

# SAILOR EDUCINATION START


class TypeDocumentNZSerializer(ModifiedRelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        return {'id': qs.id, 'name_eng': qs.name_eng, 'name_ukr': qs.name_ukr}

    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError('empty data')
        else:
            try:
                type_document_nz_id = data
            except KeyError:
                raise serializers.ValidationError('id is requid field')
            if type(type_document_nz_id) is not int:
                raise serializers.ValidationError('id must be a integer field')
            try:
                type_document_nz = TypeDocumentNZ.objects.get(id=type_document_nz_id)
                return type_document_nz
            except TypeDocumentNZ.DoesNotExist:
                raise serializers.ValidationError('TypeDocumentNZ does not exists')


class NameNZSerializer(ModifiedRelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        return {'id': qs.id, 'name_ukr': qs.name_ukr, 'name_eng': qs.name_eng}

    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError('empty data')
        else:
            try:
                name_nz = data
            except KeyError:
                raise serializers.ValidationError('id is requid field')
            if type(name_nz) is not int:
                raise serializers.ValidationError('id must be a integer field')
            try:
                nz = NZ.objects.get(id=name_nz)
                return nz
            except NZ.DoesNotExist:
                raise serializers.ValidationError('NZ does not exists')


class QualificationSerializer(ModifiedRelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        return {'id': qs.id, 'name_ukr': qs.name_ukr, 'name_eng': qs.name_eng}

    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError('empty data')
        else:
            try:
                qualification_id = data
            except KeyError:
                raise serializers.ValidationError('id is requid field')
            if type(qualification_id) is not int:
                raise serializers.ValidationError('id must be a integer field')
            try:
                nz = LevelQualification.objects.get(id=qualification_id)
                return nz
            except LevelQualification.DoesNotExist:
                raise serializers.ValidationError('LevelQualitifcation does not exists')


class SpecialitySerializer(ModifiedRelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        return {'id': qs.id, 'name_ukr': qs.name_ukr, 'name_eng': qs.name_eng}

    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError('empty data')
        else:
            try:
                spicality_id = data
            except KeyError:
                raise serializers.ValidationError('id is requid field')
            if type(spicality_id) is not int:
                raise serializers.ValidationError('id must be a integer field')
            try:
                nz = Speciality.objects.get(id=spicality_id)
                return nz
            except Speciality.DoesNotExist:
                raise serializers.ValidationError('Speciality does not exists')


class SpecializationSerializer(ModifiedRelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        return {'id': qs.id, 'speciality': qs.speciality_id, 'name_ukr': qs.name_ukr, 'name_eng': qs.name_eng}

    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError('empty data')
        else:
            try:
                specialization_id = data
            except KeyError:
                raise serializers.ValidationError('id is requid field')
            if type(specialization_id) is not int:
                raise serializers.ValidationError('id must be a integer field')
            try:
                nz = Specialization.objects.get(id=specialization_id)
                return nz
            except Specialization.DoesNotExist:
                raise serializers.ValidationError('Specialization does not exists')


class ExtentSerializer(ModifiedRelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        return {'id': qs.id, 'name_ukr': qs.name_ukr, 'name_eng': qs.name_eng}

    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError('empty data')
        else:
            try:
                extent_id = data
            except KeyError:
                raise serializers.ValidationError('id is requid field')
            if type(extent_id) is not int:
                raise serializers.ValidationError('id must be a integer field')
            try:
                nz = ExtentDiplomaUniversity.objects.get(id=extent_id)
                return nz
            except ExtentDiplomaUniversity.DoesNotExist:
                raise serializers.ValidationError('ExtentDiplomaUniversity does not exists')


# SAILOR EDUCINATION END

# QualificationDocument START


class CountrySeriallizer(ModifiedRelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        return {'id': qs.id, 'value': qs.value, 'value_eng': qs.value_eng, 'value_abbr': qs.value_abbr}

    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError('empty data')
        else:
            try:
                country = data
            except KeyError:
                raise serializers.ValidationError('id is requid field')
            if type(country) is not int:
                raise serializers.ValidationError('id must be a integer field')
            try:
                country = Country.objects.get(id=country)
                return country
            except Country.DoesNotExist:
                raise serializers.ValidationError('Country does not exists')


class TypeDocumentSerializer(ModifiedRelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        return {'id': qs.id, 'name_ukr': qs.name_ukr, 'name_eng': qs.name_eng}

    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError('empty data')
        else:
            try:
                type_document_id = data
            except KeyError:
                raise serializers.ValidationError('id is requid field')
            if type(type_document_id) is not int:
                raise serializers.ValidationError('id must be a integer field')
            try:
                type_document_nz = TypeDocument.objects.get(id=type_document_id)
                return type_document_nz
            except TypeDocument.DoesNotExist:
                raise serializers.ValidationError('TypeDocument does not exists')


class StatusDocumentSerializer(ModifiedRelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        return {'id': qs.id, 'name_ukr': qs.name_ukr, 'name_eng': qs.name_eng, 'for_service': qs.for_service}

    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError('empty data')
        else:
            try:
                status_document = data
            except KeyError:
                raise serializers.ValidationError('id is requid field')
            if type(status_document) is not int:
                raise serializers.ValidationError('id must be a integer field')
            try:
                status_document = StatusDocument.objects.get(id=status_document)
                return status_document
            except StatusDocument.DoesNotExist:
                raise serializers.ValidationError('StatusDocument does not exists')


# qualification end


class LimitationForMedicalSerializer(ModifiedRelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        response = {'id': qs.id, 'name_ukr': qs.name_ukr, 'name_eng': qs.name_eng}
        return response

    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError('empty data')
        elif type(data) is not int:
            raise serializers.ValidationError('id must be a integer field')
        else:
            try:
                id_limitation = data
                limitation = LimitationForMedical.objects.get(id=id_limitation)
                return limitation
            except LimitationForMedical.DoesNotExist:
                raise serializers.ValidationError('LimitationForMedical does not exist')


class DoctorSerializer(ModifiedRelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        response = {'id': qs.id, 'FIO': qs.FIO,
                    'medical_institution': {'id': qs.medical_institution.id, 'value': qs.medical_institution.value}}
        return response

    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError('empty data')
        elif type(data) is not int:
            raise serializers.ValidationError('id must be a integer field')
        else:
            try:
                doctor_id = data
                doctor = DoctrorInMedicalInstitution.objects.get(id=doctor_id)
                return doctor
            except DoctrorInMedicalInstitution.DoesNotExist:
                raise serializers.ValidationError('Doctor does not exist')


# medical end

# Sailor passport start

class PortSerailizer(ModifiedRelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        return {'id': qs.id, 'name_ukr': qs.name_ukr, 'name_eng': qs.name_eng}

    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError('empty data')
        elif type(data) is not int:
            raise serializers.ValidationError('id must be a integer field')
        else:
            try:
                port_id = data
            except KeyError:
                raise serializers.ValidationError('sailor is requid field')
            if type(port_id) is not int:
                raise serializers.ValidationError('port must be a integer field')
            try:
                port = Port.objects.get(id=port_id)
                return port
            except Port.DoesNotExist:
                raise serializers.ValidationError('Port does not exists')


# sailor passport end

# NTZCertificate start


class NTZSerializer(ModifiedRelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        return {'id': qs.id, 'name_ukr': qs.name_ukr, 'name_eng': qs.name_eng}

    # TO READONLY
    # disable readonly for adding ntz

    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError('empty data')
        elif type(data) is not int:
            raise serializers.ValidationError('id must be a integer field')
        else:
            try:
                ntz_id = data
            except KeyError:
                raise serializers.ValidationError('ntz is requid field')
            if type(ntz_id) is not int:
                raise serializers.ValidationError('ntz must be a integer field')
            try:
                ntz = NTZ.objects.get(id=ntz_id)
                return ntz
            except NTZ.DoesNotExist:
                raise serializers.ValidationError('NTZ does not exists')


class CourseSerializer(ModifiedRelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        return {'id': qs.id, 'name_ukr': qs.name_ukr, 'name_eng': qs.name_eng}

    # TO READONLY
    # Disable readyonly for adding ntz

    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError('empty data')
        else:
            course_id = data
            if type(course_id) is not int:
                raise serializers.ValidationError('course must be a integer field')
            try:
                course = Course.objects.get(id=course_id)
                return course
            except Course.DoesNotExist:
                raise serializers.ValidationError('Course does not exists')


class PositionForMedicalSerializer(ModifiedRelatedField):
    def to_representation(self, obj):
        if not obj:
            return []
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        response = {'id': qs.id, 'name_ukr': qs.name_ukr, 'name_eng': qs.name_eng}
        return response

    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError('empty data')
        else:
            try:
                position_id = data
            except KeyError:
                raise serializers.ValidationError('incorect dictinary')
            try:
                position = PositionForMedical.objects.get(id=position_id)
                return position
            except KeyError:
                raise serializers.ValidationError('id is requid field')
            except ValueError:
                raise serializers.ValidationError('id must be a integer field')
            except PositionForMedical.DoesNotExist:
                raise serializers.ValidationError('PositionForMedical does not exists')


class DecisionSerializer(ModifiedRelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        return {'id': qs.id, 'name_ukr': qs.name_ukr, 'name_eng': qs.name_eng}

    def to_internal_value(self, data):
        if not data:
            raise serializers.ValidationError('empty data')
        else:
            decision_id = data
            if type(decision_id) is not int:
                raise serializers.ValidationError('id must be a integer field')
            try:
                decision = Decision.objects.get(id=decision_id)
                return decision
            except Decision.DoesNotExist:
                raise serializers.ValidationError('Decision does not exists')


class FunctionAndLimitationSerializer(ModifiedRelatedField):
    def to_representation(self, value):
        resp = []
        if type(value) is list:
            for func in value:
                try:
                    qs = self.queryset.get(id=func['id_func'])
                except (TypeError, KeyError):
                    continue
                limitation = Limitations.objects.filter(id__in=func['id_limit'])
                resp.append({'function': {'id': qs.function.id, 'name_ukr': qs.function.name_ukr,
                                          'name_eng': qs.function.name_ukr},
                             'limitations': list(limitation.values('id', 'name_ukr', 'name_eng'))})
        else:
            qs = value
        return resp

    def to_internal_value(self, data):
        return data


class ProtocolDKKSerializer(ModifiedRelatedField):
    def to_representation(self, value):
        if type(value) is int:
            qs = self.queryset.get(id=value)
        else:
            qs = value
        return {'id': qs.id, 'number': qs.get_number, 'position': qs.get_position}

    def to_internal_value(self, data):
        protocol_dkk = data
        if type(protocol_dkk) is not int:
            raise serializers.ValidationError('ProtocolDKK must be a integer field')
        try:
            protocol_dkk = ProtocolSQC.objects.get(id=protocol_dkk)
            return protocol_dkk
        except ProtocolSQC.DoesNotExist:
            raise serializers.ValidationError('ProtocolDKK does not exists')


class ResponsibilityWorkBookSerializer(ModifiedRelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        return {'name_ukr': qs.name_ukr, 'name_eng': qs.name_eng, 'id': qs.id}

    def to_internal_value(self, data):
        if not data:
            return None
        else:
            function_id = data
            if type(function_id) is not int:
                raise serializers.ValidationError('Function Work Book must be a integer field')
            try:
                return ResponsibilityWorkBook.objects.get(id=function_id)
            except ResponsibilityWorkBook.DoesNotExist:
                raise serializers.ValidationError('Function Work Book does not exists')


class ResponsibilityForServiceRecordSerializer(ModifiedRelatedField):
    def to_representation(self, obj):
        if type(obj) is int:
            qs = self.queryset.get(id=obj)
        else:
            qs = obj
        return {'name_ukr': qs.name_ukr, 'name_eng': qs.name_eng, 'id': qs.id}

    def to_internal_value(self, data):
        if not data:
            return None
        else:
            function_id = data
            if type(function_id) is not int:
                raise serializers.ValidationError('Function must be a integer field')
            try:
                return Responsibility.objects.get(id=function_id)
            except Responsibility.DoesNotExist:
                raise serializers.ValidationError('Function does not exists')
