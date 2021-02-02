from datetime import datetime, date

from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status, versioning
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, force_authenticate, APIRequestFactory

from communication.models import SailorKeys
from directory.models import Position, Rank
from itcs import magic_numbers
from sailor.document.models import ServiceRecord, Education, ProtocolSQC, CertificateETI, \
    MedicalCertificate, QualificationDocument
from sailor.document.serializers import CertificateNTZSerializer, ProtocolDKKSerializer, QualificationDocumentSerializer
from sailor.document.views import ProtocolSQCView
from sailor.models import SailorPassport, DemandPositionDKK, Passport
from sailor.serializers import DemandPositionDKKSerializer, \
    CitizenPassportSerializer
from sailor.statement.models import StatementServiceRecord, StatementSQC, StatementQualification, \
    StatementSailorPassport
from sailor.statement.serializers import StatementDKKSerializer, StatementSailorPassportSerializer
from user_profile.models import UserProfile

client = APIClient()
factory_client = APIRequestFactory()

User = get_user_model()


class DeleteEducationDocumentTest(TestCase):
    databases = '__all__'
    fixtures = ['directory_fixture.json', 'agent_groups.json', 'user_profile.json', 'users.json']

    def setUp(self) -> None:
        self.sailor_key = SailorKeys.objects.create(profile=0)
        self.education = Education.objects.create(type_document_id=1,
                                                  number_document=997788,
                                                  name_nz_id=1,
                                                  status_document_id=1)
        self.sailor_key.education.append(self.education.pk)
        self.sailor_key.save(update_fields=['education'])
        user = User.objects.create_user(username='testuser', email='testuser@test.com',
                                        password='testing', is_superuser=True)
        self.token, _ = Token.objects.get_or_create(user=user)

    def test_valid_delete(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:EducationViewset-detail', kwargs={'pk': self.education.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.education.refresh_from_db()
        self.assertEqual(self.education.status_document_id, magic_numbers.STATUS_REMOVED_DOCUMENT)
        url = reverse('v1:EducationViewset-detail', kwargs={'pk': self.education.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sailor_key.refresh_from_db()
        self.assertEqual(self.sailor_key.education, [])
        self.assertEqual(Education.objects.count(), 0)

    def test_invalid_delete(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:EducationViewset-detail', kwargs={'pk': 30})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_valid_delete_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        url = reverse('v2:education-detail', kwargs={'pk': self.education.pk, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.education.refresh_from_db()
        self.assertEqual(self.education.status_document_id, magic_numbers.STATUS_REMOVED_DOCUMENT)
        url = reverse('v2:education-detail', kwargs={'pk': self.education.pk, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sailor_key.refresh_from_db()
        self.assertEqual(self.sailor_key.education, [])
        self.assertEqual(Education.objects.count(), 0)

    def test_invalid_delete_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:education-detail', kwargs={'pk': 44, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class DeleteServiceRecordTest(TestCase):
    databases = '__all__'
    fixtures = ['directory_fixture.json', 'agent_groups.json', 'user_profile.json', 'users.json']

    def setUp(self) -> None:
        self.sailor_key = SailorKeys.objects.create(profile=0)
        self.service_record = ServiceRecord.objects.create(number=1, issued_by='test',
                                                           auth_agent_ukr='auth_agent',
                                                           auth_agent_eng='auth egtn',
                                                           branch_office_id=2,
                                                           date_issued='2020-01-01',
                                                           status_document_id=2,
                                                           )
        self.sailor_key.service_records.append(self.service_record.pk)
        self.sailor_key.save(update_fields=['service_records'])
        user = User.objects.create_user(username='testuser', email='testuser@test.com',
                                        password='testing', is_superuser=True)
        self.token, _ = Token.objects.get_or_create(user=user)

    def test_valid_delete(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:service_record-detail', kwargs={'pk': self.service_record.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.service_record.refresh_from_db()
        self.assertEqual(self.service_record.status_document_id, magic_numbers.STATUS_REMOVED_DOCUMENT)
        url = reverse('v1:service_record-detail', kwargs={'pk': self.service_record.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sailor_key.refresh_from_db()
        self.assertEqual(self.sailor_key.service_records, [])
        self.assertEqual(ServiceRecord.objects.count(), 0)

    def test_valid_delete_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:service-record-detail',
                      kwargs={'pk': self.service_record.pk, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.service_record.refresh_from_db()
        self.assertEqual(self.service_record.status_document_id, magic_numbers.STATUS_REMOVED_DOCUMENT)
        url = reverse('v2:service-record-detail',
                      kwargs={'pk': self.service_record.pk, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sailor_key.refresh_from_db()
        self.assertEqual(self.sailor_key.service_records, [])
        self.assertEqual(ServiceRecord.objects.count(), 0)

    def test_invalid_delete(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:service_record-detail', kwargs={'pk': 30})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_delete_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:service-record-detail', kwargs={'pk': 30, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class DeleteStatementServiceRecordTest(TestCase):
    databases = '__all__'
    fixtures = ['directory_fixture.json', 'agent_groups.json', 'user_profile.json', 'users.json']

    def setUp(self) -> None:
        self.sailor_key = SailorKeys.objects.create(profile=0)
        self.statement_service_record = StatementServiceRecord.objects.create(
            sailor=self.sailor_key.pk,
            status_id=2,
        )
        self.sailor_key.statement_service_records.append(self.statement_service_record.pk)
        self.sailor_key.save(update_fields=['statement_service_records'])
        user = User.objects.create_user(username='testuser', email='testuser@test.com',
                                        password='testing', is_superuser=True)
        self.token, _ = Token.objects.get_or_create(user=user)

    def test_valid_delete(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:statement_service_record-detail', kwargs={'pk': self.statement_service_record.pk})
        response = client.delete(url)
        self.statement_service_record.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.statement_service_record.status_id, magic_numbers.STATUS_REMOVED_DOCUMENT)
        url = reverse('v1:statement_service_record-detail', kwargs={'pk': self.statement_service_record.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sailor_key.refresh_from_db()
        self.assertEqual(self.sailor_key.statement_service_records, [])
        self.assertEqual(StatementServiceRecord.objects.count(), 0)

    def test_invalid_delete(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:statement_service_record-detail', kwargs={'pk': 30})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_valid_delete_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:statement-service-record-detail', kwargs={'pk': self.statement_service_record.pk,
                                                                    'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.statement_service_record.refresh_from_db()
        self.assertEqual(self.statement_service_record.status_id, magic_numbers.STATUS_REMOVED_DOCUMENT)
        url = reverse('v2:statement-service-record-detail', kwargs={'pk': self.statement_service_record.pk,
                                                                    'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sailor_key.refresh_from_db()
        self.assertEqual(self.sailor_key.statement_service_records, [])
        self.assertEqual(StatementServiceRecord.objects.count(), 0)

    def test_invalid_delete_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:statement-service-record-detail', kwargs={'pk': 30, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class DeleteMedicalCertificateTest(TestCase):
    databases = '__all__'
    fixtures = ['directory_fixture.json', 'agent_groups.json', 'user_profile.json', 'users.json']

    def setUp(self) -> None:
        self.sailor_key = SailorKeys.objects.create(profile=0)
        self.medical_doc = MedicalCertificate.objects.create(
            number=0,
            position_id=1,
            limitation_id=1,
            date_start='2020-01-01',
            date_end='2020-05-05',
            doctor_id=1,
            status_document_id=2
        )
        self.sailor_key.medical_sertificate.append(self.medical_doc.pk)
        self.sailor_key.save(update_fields=['medical_sertificate'])
        user = User.objects.create_user(username='testuser', email='testuser@test.com',
                                        password='testing', is_superuser=True)
        self.token, _ = Token.objects.get_or_create(user=user)

    def test_valid_delete(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:medical_certificate-detail', kwargs={'pk': self.medical_doc.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.medical_doc.refresh_from_db()
        self.assertEqual(self.medical_doc.status_document_id, magic_numbers.STATUS_REMOVED_DOCUMENT)
        url = reverse('v1:medical_certificate-detail', kwargs={'pk': self.medical_doc.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sailor_key.refresh_from_db()
        self.assertEqual(self.sailor_key.medical_sertificate, [])
        self.assertEqual(MedicalCertificate.objects.count(), 0)

    def test_invalid_delete(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:medical_certificate-detail', kwargs={'pk': 30})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_valid_delete_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:medical-detail', kwargs={'pk': self.medical_doc.pk, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.medical_doc.refresh_from_db()
        self.assertEqual(self.medical_doc.status_document_id, magic_numbers.STATUS_REMOVED_DOCUMENT)
        url = reverse('v2:medical-detail', kwargs={'pk': self.medical_doc.pk, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.sailor_key.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.sailor_key.medical_sertificate, [])
        self.assertEqual(MedicalCertificate.objects.count(), 0)

    def test_invalid_delete_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:medical-detail', kwargs={'pk': 30, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class DeleteSailorPassportTest(TestCase):
    databases = '__all__'
    fixtures = ['directory_fixture.json', 'agent_groups.json', 'user_profile.json', 'users.json']

    def setUp(self) -> None:
        self.sailor_key = SailorKeys.objects.create(profile=0)
        self.sailor_passport = SailorPassport.objects.create(
            country_id=2,
            number_document=0,
            date_start='2020-01-01',
            date_end='2025-01-01',
            captain='captain',
            status_document_id=2,
        )
        self.sailor_key.sailor_passport.append(self.sailor_passport.pk)
        self.sailor_key.save(update_fields=['sailor_passport'])
        user = User.objects.create_user(username='testuser', email='testuser@test.com',
                                        password='testing', is_superuser=True)
        self.token, _ = Token.objects.get_or_create(user=user)

    def test_valid_delete(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:sailor-passport-detail', kwargs={'pk': self.sailor_passport.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sailor_passport.refresh_from_db()
        self.assertEqual(self.sailor_passport.status_document_id, magic_numbers.STATUS_REMOVED_DOCUMENT)
        url = reverse('v1:sailor-passport-detail', kwargs={'pk': self.sailor_passport.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sailor_key.refresh_from_db()
        self.assertEqual(self.sailor_key.sailor_passport, [])
        self.assertEqual(SailorPassport.objects.count(), 0)

    def test_invalid_delete(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:sailor-passport-detail', kwargs={'pk': 30})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_valid_delete_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:sailor-passport-detail', kwargs={'pk': self.sailor_passport.pk,
                                                           'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sailor_passport.refresh_from_db()
        self.assertEqual(self.sailor_passport.status_document_id, magic_numbers.STATUS_REMOVED_DOCUMENT)
        url = reverse('v2:sailor-passport-detail', kwargs={'pk': self.sailor_passport.pk,
                                                           'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sailor_key.refresh_from_db()
        self.assertEqual(self.sailor_key.sailor_passport, [])
        self.assertEqual(SailorPassport.objects.count(), 0)

    def test_invalid_delete_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:sailor-passport-detail', kwargs={'pk': 30, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CertificateNTZViewsetTest(TestCase):
    databases = '__all__'
    fixtures = ['directory_fixture.json', 'agent_groups.json', 'user_profile.json', 'users.json']

    def setUp(self) -> None:
        self.sailor_key = SailorKeys.objects.create(profile=0)
        self.certificate_ntz = CertificateETI.objects.create(
            ntz_id=1,
            ntz_number=1,
            course_training_id=4,
            date_start='2020-01-01',
            date_end='2025-01-01',
            status_document_id=2,
        )
        self.sailor_key.sertificate_ntz.append(self.certificate_ntz.pk)
        self.sailor_key.save(update_fields=['sertificate_ntz'])
        user = User.objects.create_user(username='testuser', email='testuser@test.com',
                                        password='testing', is_superuser=True)
        self.token, _ = Token.objects.get_or_create(user=user)

    def test_list_of_certificates(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:certificate-eti-sailor-list', kwargs={'pk': self.sailor_key.pk})
        response = client.get(url)
        self.assertEqual(len(response.data), 1)
        ntz_info = [CertificateNTZSerializer(instance=self.certificate_ntz).data]
        self.assertEqual(response.data, ntz_info)

    def test_list_of_certificates_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:certificate-list', kwargs={'sailor_pk': self.sailor_key.pk})
        response = client.get(url)
        self.assertEqual(len(response.data), 1)
        ntz_info = [CertificateNTZSerializer(instance=self.certificate_ntz).data]
        self.assertEqual(response.data, ntz_info)

    def test_valid_delete_certificate(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:certificate-eti-detail', kwargs={'pk': self.certificate_ntz.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.certificate_ntz.refresh_from_db()
        self.assertEqual(self.certificate_ntz.status_document_id, magic_numbers.STATUS_REMOVED_DOCUMENT)
        url = reverse('v1:certificate-eti-detail', kwargs={'pk': self.certificate_ntz.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sailor_key.refresh_from_db()
        self.assertEqual(self.sailor_key.sertificate_ntz, [])
        self.assertEqual(CertificateETI.objects.count(), 0)

    def test_valid_delete_certificate_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:certificate-detail', kwargs={'pk': self.certificate_ntz.pk, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.certificate_ntz.refresh_from_db()
        self.assertEqual(self.certificate_ntz.status_document_id, magic_numbers.STATUS_REMOVED_DOCUMENT)
        url = reverse('v2:certificate-detail', kwargs={'pk': self.certificate_ntz.pk, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sailor_key.refresh_from_db()
        self.assertEqual(self.sailor_key.sertificate_ntz, [])
        self.assertEqual(CertificateETI.objects.count(), 0)

    def test_invalid_delete_certificate(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:certificate-eti-detail', kwargs={'pk': 30})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_delete_certificate_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:certificate-detail', kwargs={'pk': 30, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class StatementDKKViewsetTest(TestCase):
    databases = '__all__'
    fixtures = ['directory_fixture.json', 'agent_groups.json', 'user_profile.json', 'users.json']

    def setUp(self) -> None:
        self.sailor_key = SailorKeys.objects.create(profile=0)
        user = User.objects.create_user(username='testuser', email='testuser@test.com',
                                        password='testing', is_superuser=True)
        UserProfile.objects.create(user=user, type_user=UserProfile.BACK_OFFICE)
        self.statement_sqc = StatementSQC.objects.create(
            number=1,
            sailor=self.sailor_key.pk,
            rank_id=98,
            list_positions=[123],
            status_document_id=2,
            branch_office_id=2,

        )
        self.protocol_dkk = ProtocolSQC.objects.create(
            statement_dkk=self.statement_sqc,
            number_document=1,
            date_meeting='2020-01-01',
            branch_create_id=2,
            status_document_id=2,
            decision_id=2,
            author=user,
        )
        self.sailor_key.statement_dkk.append(self.statement_sqc.pk)
        self.sailor_key.save(update_fields=['statement_dkk'])
        self.token, _ = Token.objects.get_or_create(user=user)

    def test_get_queryset_without_sailor(self):
        self.statement_without_sailor = self.statement_sqc
        self.statement_without_sailor.pk = None
        self.statement_without_sailor.sailor = 0
        self.statement_without_sailor.save()
        self.sailor_key.statement_dkk.append(self.statement_without_sailor.pk)
        self.sailor_key.save(update_fields=['statement_dkk'])
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:statement-sqc-sailor-list', kwargs={'pk': self.sailor_key.pk})
        client.get(url)
        self.statement_without_sailor.refresh_from_db()
        self.assertEqual(self.statement_without_sailor.sailor, self.sailor_key.pk)

    def test_get_queryset_without_sailor_v2(self):
        self.statement_without_sailor = self.statement_sqc
        self.statement_without_sailor.pk = None
        self.statement_without_sailor.sailor = 0
        self.statement_without_sailor.save()
        self.sailor_key.statement_dkk.append(self.statement_without_sailor.pk)
        self.sailor_key.save(update_fields=['statement_dkk'])
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:statement-sqc-list', kwargs={'sailor_pk': self.sailor_key.pk})
        client.get(url)
        self.statement_without_sailor.refresh_from_db()
        self.assertEqual(self.statement_without_sailor.sailor, self.sailor_key.pk)

    def test_list_of_statement_dkk(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:statement-sqc-sailor-list', kwargs={'pk': self.sailor_key.pk})
        response = client.get(url)
        self.assertEqual(len(response.data), 1)
        ntz_info = [StatementDKKSerializer(instance=self.statement_sqc).data]
        self.assertEqual(response.data, ntz_info)

    def test_list_of_certificates_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:statement-sqc-list', kwargs={'sailor_pk': self.sailor_key.pk})
        response = client.get(url)
        self.assertEqual(len(response.data), 1)
        ntz_info = [StatementDKKSerializer(instance=self.statement_sqc).data]
        self.assertEqual(response.data, ntz_info)

    def test_invalid_delete_with_protocol(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:statement-sqc-detail', kwargs={'pk': self.statement_sqc.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.protocol_dkk.delete()

    def test_invalid_delete_with_protocol_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:statement-sqc-detail', kwargs={'pk': self.statement_sqc.pk, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.protocol_dkk.delete()

    def test_valid_delete_statement(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.protocol_dkk.delete()
        url = reverse('v1:statement-sqc-detail', kwargs={'pk': self.statement_sqc.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.statement_sqc.refresh_from_db()
        self.assertEqual(self.statement_sqc.status_document_id, magic_numbers.STATUS_REMOVED_DOCUMENT)
        url = reverse('v1:statement-sqc-detail', kwargs={'pk': self.statement_sqc.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sailor_key.refresh_from_db()
        self.assertEqual(self.sailor_key.statement_dkk, [])
        self.assertEqual(StatementSQC.objects.count(), 0)

    def test_valid_delete_statement_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.protocol_dkk.delete()
        url = reverse('v2:statement-sqc-detail', kwargs={'pk': self.statement_sqc.pk, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.statement_sqc.refresh_from_db()
        self.assertEqual(self.statement_sqc.status_document_id, magic_numbers.STATUS_REMOVED_DOCUMENT)
        url = reverse('v2:statement-sqc-detail', kwargs={'pk': self.statement_sqc.pk, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sailor_key.refresh_from_db()
        self.assertEqual(self.sailor_key.statement_dkk, [])
        self.assertEqual(StatementSQC.objects.count(), 0)

    def test_invalid_delete_statement_dkk(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:statement-sqc-detail', kwargs={'pk': 30})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_delete_statement_dkk_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:statement-sqc-detail', kwargs={'pk': 30, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class DemandPositionViewsetTest(TestCase):
    databases = '__all__'
    fixtures = ['directory_fixture.json', 'agent_groups.json', 'user_profile.json', 'users.json']

    def setUp(self) -> None:
        self.sailor_key = SailorKeys.objects.create(profile=0)
        self.demand_position = DemandPositionDKK.objects.create(
            list_positions=[123],
            rank_id=98,
            status_document_id=2,
        )
        self.sailor_key.demand_position.append(self.demand_position.pk)
        self.sailor_key.save(update_fields=['demand_position'])
        user = User.objects.create_user(username='testuser', email='testuser@test.com',
                                        password='testing', is_superuser=True)
        self.token, _ = Token.objects.get_or_create(user=user)

    def test_list_of_demands(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:demand-position-sailor-list', kwargs={'pk': self.sailor_key.pk})
        response = client.get(url)
        self.assertEqual(len(response.data), 1)
        demand_info = [DemandPositionDKKSerializer(instance=self.demand_position).data]
        self.assertEqual(response.data, demand_info)

    def test_list_of_demands_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:demand-list', kwargs={'sailor_pk': self.sailor_key.pk})
        response = client.get(url)
        self.assertEqual(len(response.data), 1)
        demand_info = [DemandPositionDKKSerializer(instance=self.demand_position).data]
        self.assertEqual(response.data, demand_info)

    def test_get_demand(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:demand-position-detail', kwargs={'pk': self.demand_position.pk})
        response = client.get(url)
        demand_info = DemandPositionDKKSerializer(instance=self.demand_position).data
        self.assertEqual(response.data, demand_info)

    def test_get_demand_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:demand-detail', kwargs={'pk': self.demand_position.pk, 'sailor_pk': self.sailor_key.pk})
        response = client.get(url)
        demand_info = DemandPositionDKKSerializer(instance=self.demand_position).data
        self.assertEqual(response.data, demand_info)

    def test_valid_delete_demand(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:demand-position-detail', kwargs={'pk': self.demand_position.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.demand_position.refresh_from_db()
        self.assertEqual(self.demand_position.status_document_id, magic_numbers.STATUS_REMOVED_DOCUMENT)
        url = reverse('v1:demand-position-detail', kwargs={'pk': self.demand_position.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sailor_key.refresh_from_db()
        self.assertEqual(self.sailor_key.demand_position, [])
        self.assertEqual(DemandPositionDKK.objects.count(), 0)

    def test_valid_delete_demand_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:demand-detail', kwargs={'pk': self.demand_position.pk, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.demand_position.refresh_from_db()
        self.assertEqual(self.demand_position.status_document_id, magic_numbers.STATUS_REMOVED_DOCUMENT)
        url = reverse('v2:demand-detail', kwargs={'pk': self.demand_position.pk, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sailor_key.refresh_from_db()
        self.assertEqual(self.sailor_key.demand_position, [])
        self.assertEqual(DemandPositionDKK.objects.count(), 0)

    def test_invalid_delete_certificate(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:demand-position-detail', kwargs={'pk': 30})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_delete_certificate_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:demand-detail', kwargs={'pk': 30, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CitizenPassportTestViewsetTest(TestCase):
    databases = '__all__'
    fixtures = ['directory_fixture.json', 'agent_groups.json', 'user_profile.json', 'users.json']

    def setUp(self) -> None:
        self.sailor_key = SailorKeys.objects.create(profile=0)
        self.passport = Passport.objects.create(
            serial='СЕ44444',
            date='2020-01-01',
            issued_by='Issued by',
            country_id=2,
            inn='44444',
            city_birth_id=10507,
            country_birth_id=2
        )
        self.sailor_key.citizen_passport.append(self.passport.pk)
        self.sailor_key.save(update_fields=['citizen_passport'])
        user = User.objects.create_user(username='testuser', email='testuser@test.com',
                                        password='testing', is_superuser=True)
        self.token, _ = Token.objects.get_or_create(user=user)

    def test_list_of_citizen_passport(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:citizen-passport-sailor-list', kwargs={'pk': self.sailor_key.pk})
        response = client.get(url)
        self.assertEqual(len(response.data), 1)
        demand_info = [CitizenPassportSerializer(instance=self.passport).data]
        self.assertEqual(response.data, demand_info)

    def test_list_of_citizen_passport_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:citizen-passport-list', kwargs={'sailor_pk': self.sailor_key.pk})
        response = client.get(url)
        self.assertEqual(len(response.data), 1)
        demand_info = [CitizenPassportSerializer(instance=self.passport).data]
        self.assertEqual(response.data, demand_info)

    def test_get_citizen_passport(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:citizen-passport-detail', kwargs={'pk': self.passport.pk})
        response = client.get(url)
        demand_info = CitizenPassportSerializer(instance=self.passport).data
        self.assertEqual(response.data, demand_info)

    def test_get_citizen_passport_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:citizen-passport-detail', kwargs={'pk': self.passport.pk, 'sailor_pk': self.sailor_key.pk})
        response = client.get(url)
        demand_info = CitizenPassportSerializer(instance=self.passport).data
        self.assertEqual(response.data, demand_info)

    def test_valid_delete_passport(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:citizen-passport-detail', kwargs={'pk': self.passport.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sailor_key.refresh_from_db()
        self.assertEqual(self.sailor_key.citizen_passport, [])
        self.assertEqual(Passport.objects.count(), 0)

    def test_valid_delete_passport_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:citizen-passport-detail', kwargs={'pk': self.passport.pk, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sailor_key.refresh_from_db()
        self.assertEqual(self.sailor_key.citizen_passport, [])
        self.assertEqual(Passport.objects.count(), 0)

    def test_invalid_delete_passport(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:citizen-passport-detail', kwargs={'pk': 30})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_delete_passport_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:citizen-passport-detail', kwargs={'pk': 30, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProtocolDKKTestViewsetTest(TestCase):
    databases = '__all__'
    fixtures = ['directory_fixture.json', 'agent_groups.json', 'user_profile.json', 'users.json']

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', email='testuser@test.com',
                                             password='testing', is_superuser=True)
        self.sailor_key = SailorKeys.objects.create(profile=0)
        self.statement_sqc = StatementSQC.objects.create(
            number=1,
            sailor=self.sailor_key.pk,
            rank_id=98,
            list_positions=[123],
            status_document_id=2,
            branch_office_id=2,
        )
        self.protocol_dkk = ProtocolSQC.objects.create(
            statement_dkk=self.statement_sqc,
            number_document=1,
            date_meeting=date(2020, 1, 1),
            branch_create_id=2,
            status_document_id=2,
            decision_id=2,
            author=self.user,
        )
        self.sailor_key.protocol_dkk.append(self.protocol_dkk.pk)
        self.sailor_key.save(update_fields=['protocol_dkk'])
        self.token, _ = Token.objects.get_or_create(user=self.user)

    def test_list_protocol_dkk(self):
        class FakeResolverMatch:
            namespace = 'v1'

        scheme = versioning.NamespaceVersioning
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        view = ProtocolSQCView.as_view({'get': 'list'}, versioning_class=scheme)
        url = reverse('v1:protocol-dkk-sailor-list', kwargs={'pk': self.sailor_key.pk})
        request = factory_client.get(url)
        request.resolver_match = FakeResolverMatch
        force_authenticate(request, user=self.user)
        response = view(request, pk=self.sailor_key.pk, version='v1')
        self.assertEqual(len(response.data), 1)
        protocol_info = [ProtocolDKKSerializer(instance=self.protocol_dkk, context={'request': request}).data]
        self.assertEqual(response.data, protocol_info)

    def test_list_protocol_dkk_v2(self):
        class FakeResolverMatch:
            namespace = 'v2'

        scheme = versioning.NamespaceVersioning
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        view = ProtocolSQCView.as_view({'get': 'list'}, versioning_class=scheme)
        url = reverse('v2:protocol-sqc-list', kwargs={'sailor_pk': self.sailor_key.pk})
        request = factory_client.get(url)
        request.resolver_match = FakeResolverMatch
        force_authenticate(request, user=self.user)
        response = view(request, sailor_pk=self.sailor_key.pk, version='v2')
        self.assertEqual(len(response.data), 1)
        protocol_info = [ProtocolDKKSerializer(instance=self.protocol_dkk, context={'request': request}).data]
        self.assertEqual(response.data, protocol_info)

    def test_get_protocol_dkk(self):
        class FakeResolverMatch:
            namespace = 'v1'

        scheme = versioning.NamespaceVersioning

        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        view = ProtocolSQCView.as_view({'get': 'retrieve'}, versioning_class=scheme)
        url = reverse('v1:protocol-dkk-sailor-list', kwargs={'pk': self.sailor_key.pk})
        request = factory_client.get(url)
        request.resolver_match = FakeResolverMatch
        force_authenticate(request, user=self.user)
        response = view(request, pk=self.protocol_dkk.pk, versioning='v1')
        protocol_info = ProtocolDKKSerializer(instance=self.protocol_dkk, context={'request': request}).data
        self.assertEqual(response.data, protocol_info)

    def test_get_protocol_dkk_v2(self):
        class FakeResolverMatch:
            namespace = 'v2'

        scheme = versioning.NamespaceVersioning

        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        view = ProtocolSQCView.as_view({'get': 'retrieve'}, versioning_class=scheme)
        url = reverse('v2:protocol-sqc-detail', kwargs={'pk': self.protocol_dkk.pk, 'sailor_pk': self.sailor_key.pk})
        request = factory_client.get(url)
        force_authenticate(request, user=self.user)
        request.resolver_match = FakeResolverMatch
        response = view(request, pk=self.protocol_dkk.pk, versioning='v2')
        protocol_info = ProtocolDKKSerializer(instance=self.protocol_dkk, context={'request': request}).data
        self.assertEqual(response.data, protocol_info)

    def test_invalid_delete_with_statement_qual_protocol(self):
        StatementQualification.objects.create(
            protocol_dkk=self.protocol_dkk,
            number=1,
            sailor=0,
            rank_id=98,
            list_positions=[123],
            status_document_id=2,
            port_id=1,
            author=self.user
        )
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:protocol-dkk-detail', kwargs={'pk': self.protocol_dkk.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_with_statement_qual_protocol_v2(self):
        StatementQualification.objects.create(
            protocol_dkk=self.protocol_dkk,
            number=1,
            sailor=0,
            rank_id=98,
            list_positions=[123],
            status_document_id=2,
            port_id=1,
            author=self.user
        )
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:protocol-sqc-detail', kwargs={'pk': self.protocol_dkk.pk, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_delete_protocol(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:protocol-dkk-detail', kwargs={'pk': self.protocol_dkk.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.protocol_dkk.refresh_from_db()
        self.assertEqual(self.protocol_dkk.status_document_id, magic_numbers.STATUS_REMOVED_DOCUMENT)
        url = reverse('v1:protocol-dkk-detail', kwargs={'pk': self.protocol_dkk.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sailor_key.refresh_from_db()
        self.assertEqual(self.sailor_key.protocol_dkk, [])
        self.assertEqual(ProtocolSQC.objects.count(), 0)

    def test_valid_delete_protocol_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:protocol-sqc-detail', kwargs={'pk': self.protocol_dkk.pk, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.protocol_dkk.refresh_from_db()
        self.assertEqual(self.protocol_dkk.status_document_id, magic_numbers.STATUS_REMOVED_DOCUMENT)
        url = reverse('v2:protocol-sqc-detail', kwargs={'pk': self.protocol_dkk.pk, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sailor_key.refresh_from_db()
        self.assertEqual(self.sailor_key.protocol_dkk, [])
        self.assertEqual(ProtocolSQC.objects.count(), 0)

    def test_invalid_delete_protocol(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:protocol-dkk-detail', kwargs={'pk': 30})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_delete_protocol_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:protocol-sqc-detail', kwargs={'pk': 30, 'sailor_pk': self.sailor_key})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class QualificationDocumentTestViewsetTest(TestCase):
    databases = '__all__'
    fixtures = ['directory_fixture.json', 'agent_groups.json', 'user_profile.json', 'users.json']

    def setUp(self) -> None:
        self.sailor_key = SailorKeys.objects.create(profile=0)
        self.qual_doc = QualificationDocument.objects.create(
            number_document=0,
            list_positions=[123],
            rank_id=23,
            date_start='2020-01-01',
            type_document_id=87,
            status_document_id=2,

        )
        self.sailor_key.qualification_documents.append(self.qual_doc.pk)
        self.sailor_key.save(update_fields=['qualification_documents'])
        user = User.objects.create_user(username='testuser', email='testuser@test.com',
                                        password='testing', is_superuser=True)
        UserProfile.objects.create(user=user, type_user=UserProfile.BACK_OFFICE)
        self.token, _ = Token.objects.get_or_create(user=user)

    def test_valid_delete(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:qualification-document-detail', kwargs={'pk': self.qual_doc.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.qual_doc.refresh_from_db()
        self.assertEqual(self.qual_doc.status_document_id, magic_numbers.STATUS_REMOVED_DOCUMENT)
        url = reverse('v1:qualification-document-detail', kwargs={'pk': self.qual_doc.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sailor_key.refresh_from_db()
        self.assertEqual(self.sailor_key.qualification_documents, [])
        self.assertEqual(QualificationDocument.objects.count(), 0)

    def test_valid_delete_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:qualification-detail', kwargs={'pk': self.qual_doc.pk, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.qual_doc.refresh_from_db()
        self.assertEqual(self.qual_doc.status_document_id, magic_numbers.STATUS_REMOVED_DOCUMENT)
        url = reverse('v2:qualification-detail', kwargs={'pk': self.qual_doc.pk, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sailor_key.refresh_from_db()
        self.assertEqual(self.sailor_key.qualification_documents, [])
        self.assertEqual(QualificationDocument.objects.count(), 0)

    def test_invalid_delete(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:qualification-document-detail', kwargs={'pk': 30})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_delete_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:qualification-detail', kwargs={'pk': 30, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_qual_docs(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:qualification-document-sailor-list', kwargs={'pk': self.sailor_key.pk})
        response = client.get(url)
        self.assertEqual(len(response.data), 1)
        qual_doc_info = [QualificationDocumentSerializer(instance=self.qual_doc).data]
        self.assertEqual(response.data, qual_doc_info)

    def test_list_qual_docs_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:qualification-list', kwargs={'sailor_pk': self.sailor_key.pk})
        response = client.get(url)
        self.assertEqual(len(response.data), 1)
        qual_doc_info = [QualificationDocumentSerializer(instance=self.qual_doc).data]
        self.assertEqual(response.data, qual_doc_info)

    def test_get_qual_doc(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:qualification-document-detail', kwargs={'pk': self.qual_doc.pk})
        response = client.get(url)
        qual_doc_info = QualificationDocumentSerializer(instance=self.qual_doc).data
        self.assertEqual(response.data, qual_doc_info)

    def test_get_qual_doc_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:qualification-detail', kwargs={'pk': self.qual_doc.pk, 'sailor_pk': self.sailor_key.pk})
        response = client.get(url)
        qual_doc_info = QualificationDocumentSerializer(instance=self.qual_doc).data
        self.assertEqual(response.data, qual_doc_info)


class TestAvailablePositionForSailor(TestCase):
    databases = '__all__'
    fixtures = ['position_with_depend.json', 'directory_fixture.json', 'agent_groups.json', 'user_profile.json',
                'users.json']

    def setUp(self) -> None:
        self.sailor_key = SailorKeys.objects.create(profile=0)
        self.position = Position.objects.get(id=123)
        self.qual_doc = QualificationDocument.objects.create(
            number_document=0,
            list_positions=[self.position.pk],
            rank_id=98,
            date_start='2020-01-01',
            type_document_id=87,
            status_document_id=19,

        )
        self.sailor_key.qualification_documents.append(self.qual_doc.pk)
        self.sailor_key.save(update_fields=['qualification_documents'])
        user = User.objects.create_user(username='testuser', email='testuser@test.com',
                                        password='testing', is_superuser=True)
        self.token, _ = Token.objects.get_or_create(user=user)

    def test_valid_available_position_for_sailor(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:available-position-sailor', kwargs={'pk': self.sailor_key.pk})
        response = client.get(url)
        valid_positions = set(self.position.allowed_to_get.values_list('pk', flat=True))
        valid_ranks = set(Rank.objects.filter(
            position__in=valid_positions, is_disable=False).values_list('pk', flat=True))
        valid_ranks = valid_ranks.union({98, 23, 83, 87, 86, 90, 95, 97, 99, 100, 144, 145, 103, 123, 121, 104, 127})
        valid_positions = valid_positions.union(
            {123, 63, 81, 221, 87, 96, 101, 103, 105, 106, 184, 185, 151, 150, 149, 145, 144, 152, 133})
        self.assertCountEqual(response.data['rank'], valid_ranks)
        self.assertCountEqual(response.data['position'], valid_positions)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_valid_available_position_for_sailor_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:available-position-detail', kwargs={'sailor_pk': self.sailor_key.pk, })
        response = client.get(url)
        valid_positions = set(self.position.allowed_to_get.values_list('pk', flat=True))
        valid_ranks = set(Rank.objects.filter(
            position__in=valid_positions, is_disable=False).values_list('pk', flat=True))
        valid_ranks = valid_ranks.union({98, 23, 83, 87, 86, 90, 95, 97, 99, 100, 144, 145, 103, 123, 121, 104, 127})
        valid_positions = valid_positions.union(
            {123, 63, 81, 221, 87, 96, 101, 103, 105, 106, 184, 185, 151, 150, 149, 145, 144, 152, 133})
        self.assertCountEqual(response.data['rank'], list(valid_ranks))
        self.assertCountEqual(response.data['position'], list(valid_positions))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class StatementSailorPassportViewsetTest(TestCase):
    """Проверка списка заявлений на ПОМ"""
    databases = '__all__'
    fixtures = ['directory_fixture.json', 'agent_groups.json', 'user_profile.json', 'users.json',
                'status_document_statement_sailor_passport.json']

    def setUp(self) -> None:
        self.sailor_key = SailorKeys.objects.create(profile=0)
        user = User.objects.create_user(username='testuser', email='testuser@test.com',
                                        password='testing', is_superuser=True)
        self.statement_sailor_passport = StatementSailorPassport.objects.create(
            number=1,
            port_id=1,
            is_payed=False,
            status_document_id=magic_numbers.status_statement_sailor_passport_in_process,
            sailor_passport=None,
            type_receipt=2
        )
        self.sailor_key.statement_sailor_passport.append(self.statement_sailor_passport.pk)
        self.sailor_key.save(update_fields=['statement_sailor_passport'])
        self.token, _ = Token.objects.get_or_create(user=user)

    def test_list_of_statement_sailor_passport(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:statement-sailor-passport-sailor-list', kwargs={'pk': self.sailor_key.pk})
        response = client.get(url)
        self.assertEqual(len(response.data), 1)
        statement_info = [StatementSailorPassportSerializer(instance=self.statement_sailor_passport).data]
        self.assertEqual(response.data, statement_info)

    def test_list_of_statement_sailor_passport_v2(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:statement-sailor-passport-list', kwargs={'sailor_pk': self.sailor_key.pk})
        response = client.get(url)
        self.assertEqual(len(response.data), 1)
        statement_info = [StatementSailorPassportSerializer(instance=self.statement_sailor_passport).data]
        self.assertEqual(response.data, statement_info)


class DeleteStatementSailorPassportViewsetTest(TestCase):
    """Удаление заявлений на ПОМ"""
    databases = '__all__'
    fixtures = ['directory_fixture.json', 'agent_groups.json', 'user_profile.json', 'users.json',
                'status_document_statement_sailor_passport.json']

    def setUp(self) -> None:
        self.sailor_key = SailorKeys.objects.create(profile=0)
        user = User.objects.create_user(username='testuser', email='testuser@test.com',
                                        password='testing', is_superuser=True)
        self.statement_sailor_passport = StatementSailorPassport.objects.create(
            number=1,
            port_id=1,
            is_payed=False,
            status_document_id=magic_numbers.status_statement_sailor_passport_in_process,
            sailor_passport=None,
            type_receipt=2
        )
        self.sailor_key.statement_sailor_passport.append(self.statement_sailor_passport.pk)
        self.sailor_key.save(update_fields=['statement_sailor_passport'])
        self.token, _ = Token.objects.get_or_create(user=user)

    def test_invalid_delete_statement_sailor_passport(self):
        """Удаление несуществующей записи"""
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:statement-sailor-passport-detail', kwargs={'pk': 30})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_delete_statement_sailor_passport_v2(self):
        """Удаление несуществующей записи"""
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:statement-sailor-passport-detail', kwargs={'pk': 30, 'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_valid_delete_statement(self):
        """Успешное удаление записи"""
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:statement-sailor-passport-detail', kwargs={'pk': self.statement_sailor_passport.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.statement_sailor_passport.refresh_from_db()
        self.assertEqual(self.statement_sailor_passport.status_document_id, magic_numbers.STATUS_REMOVED_DOCUMENT)
        url = reverse('v1:statement-sailor-passport-detail', kwargs={'pk': self.statement_sailor_passport.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sailor_key.refresh_from_db()
        self.assertEqual(self.sailor_key.statement_sailor_passport, [])
        self.assertEqual(StatementSailorPassport.objects.count(), 0)

    def test_valid_delete_statement_v2(self):
        """Успешное удаление записи"""
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:statement-sailor-passport-detail', kwargs={'pk': self.statement_sailor_passport.pk,
                                                                     'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.statement_sailor_passport.refresh_from_db()
        self.assertEqual(self.statement_sailor_passport.status_document_id, magic_numbers.STATUS_REMOVED_DOCUMENT)
        url = reverse('v2:statement-sailor-passport-detail', kwargs={'pk': self.statement_sailor_passport.pk,
                                                                     'sailor_pk': self.sailor_key.pk})
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.sailor_key.refresh_from_db()
        self.assertEqual(self.sailor_key.statement_sailor_passport, [])
        self.assertEqual(StatementSailorPassport.objects.count(), 0)


class CreateContinueStatementSailorPassportViewsetTest(TestCase):
    """Создание заявления ПОМ, продолжение ПОМ"""
    databases = '__all__'
    fixtures = ['directory_fixture.json', 'agent_groups.json', 'user_profile.json', 'users.json',
                'status_document_statement_sailor_passport.json']

    def setUp(self) -> None:
        self.sailor_key = SailorKeys.objects.create(profile=0)
        user = User.objects.create_user(username='testuser', email='testuser@test.com',
                                        password='testing', is_superuser=True)
        self.sailor_passport = SailorPassport.objects.create(
            country_id=2,
            number_document=0,
            date_start=datetime.strptime('2020-01-01', '%Y-%m-%d').date(),
            date_end=datetime.strptime('2025-01-01', '%Y-%m-%d').date(),
            captain='captain',
            status_document_id=magic_numbers.status_service_record_valid,
        )
        self.sailor_key.sailor_passport.append(self.sailor_passport.pk)
        self.sailor_key.save(update_fields=['sailor_passport'])
        self.token, _ = Token.objects.get_or_create(user=user)

    def test_create_valid_statement_sailor_passport(self):
        """Успешное создание заявленя на ПОМ"""
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:statement-sailor-passport-list')
        response = client.post(url, data={'port': 1, 'sailor': self.sailor_key.pk, 'type_receipt': 4})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.sailor_key.refresh_from_db()
        self.assertEqual(len(self.sailor_key.statement_sailor_passport), 1)
        statement = StatementSailorPassport.objects.get(id=self.sailor_key.statement_sailor_passport[0])
        self.assertEqual(statement.is_continue, True)

    def test_create_valid_statement_sailor_passport_v2(self):
        """Успешное создание заявленя на ПОМ"""
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:statement-sailor-passport-list', kwargs={'sailor_pk': self.sailor_key.pk})
        response = client.post(url, data={'port': 1, 'sailor': self.sailor_key.pk, 'type_receipt': 4})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.sailor_key.refresh_from_db()
        self.assertEqual(len(self.sailor_key.statement_sailor_passport), 1)
        statement = StatementSailorPassport.objects.get(id=self.sailor_key.statement_sailor_passport[0])
        self.assertEqual(statement.is_continue, True)


class CreateApprovStatementSailorPassportViewsetTest(TestCase):
    """Создание заявления ПОМ, при переводе в статус Схвалено будет создана новая ПОМ"""
    databases = '__all__'
    fixtures = ['directory_fixture.json', 'agent_groups.json', 'user_profile.json', 'users.json',
                'status_document_statement_sailor_passport.json']

    def setUp(self) -> None:
        self.sailor_key = SailorKeys.objects.create(profile=0)
        user = User.objects.create_user(username='testuser', email='testuser@test.com',
                                        password='testing', is_superuser=True)
        self.sailor_passport = SailorPassport.objects.create(
            country_id=2,
            number_document=0,
            date_start=datetime.strptime('2020-01-01', '%Y-%m-%d').date(),
            date_end=datetime.strptime('2025-01-01', '%Y-%m-%d').date(),
            captain='captain',
            status_document_id=magic_numbers.status_qual_doc_expired,
        )
        self.sailor_key.sailor_passport.append(self.sailor_passport.pk)
        self.sailor_key.save(update_fields=['sailor_passport'])
        self.token, _ = Token.objects.get_or_create(user=user)

    def test_create_valid_statement_sailor_passport(self):
        """Успешное создание заявленя на ПОМ"""
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:statement-sailor-passport-list')
        response = client.post(url, data={'port': 1, 'sailor': self.sailor_key.pk, 'type_receipt': 2})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.sailor_key.refresh_from_db()
        self.assertEqual(len(self.sailor_key.statement_sailor_passport), 1)
        statement = StatementSailorPassport.objects.get(id=self.sailor_key.statement_sailor_passport[0])
        self.assertEqual(statement.is_continue, False)

    def test_create_valid_statement_sailor_passport_v2(self):
        """Успешное создание заявленя на ПОМ"""
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:statement-sailor-passport-list', kwargs={'sailor_pk': self.sailor_key.pk})
        response = client.post(url, data={'port': 1, 'sailor': self.sailor_key.pk, 'type_receipt': 2})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.sailor_key.refresh_from_db()
        self.assertEqual(len(self.sailor_key.statement_sailor_passport), 1)
        statement = StatementSailorPassport.objects.get(id=self.sailor_key.statement_sailor_passport[0])
        self.assertEqual(statement.is_continue, False)


class UpdateContinueStatementSailorPassportViewsetTest(TestCase):
    """Обновление заявления на ПОМ, продление ПОМ"""
    databases = '__all__'
    fixtures = ['directory_fixture.json', 'agent_groups.json', 'user_profile.json', 'users.json',
                'status_document_statement_sailor_passport.json']

    def setUp(self) -> None:
        self.sailor_key = SailorKeys.objects.create(profile=0)
        user = User.objects.create_user(username='testuser', email='testuser@test.com',
                                        password='testing', is_superuser=True)
        self.sailor_passport = SailorPassport.objects.create(
            country_id=2,
            number_document=1,
            date_start=datetime.strptime('2020-01-01', '%Y-%m-%d').date(),
            date_end=datetime.strptime('2025-01-01', '%Y-%m-%d').date(),
            captain='captain',
            status_document_id=magic_numbers.status_service_record_valid,
        )
        self.statement_sailor_passport = StatementSailorPassport.objects.create(
            number=1,
            port_id=1,
            is_payed=False,
            is_continue=True,
            status_document_id=magic_numbers.status_statement_sailor_passport_in_process,
            sailor_passport=self.sailor_passport,
            type_receipt=4,
        )
        self.sailor_key.statement_sailor_passport.append(self.statement_sailor_passport.pk)
        self.sailor_key.sailor_passport.append(self.sailor_passport.pk)
        self.sailor_key.save(update_fields=['statement_sailor_passport', 'sailor_passport'])
        self.token, _ = Token.objects.get_or_create(user=user)

    def test_invalid_update_statement_sailor_passport(self):
        """Заявление не оплачено, меняем статус на Схвалено"""
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:statement-sailor-passport-detail', kwargs={'pk': self.statement_sailor_passport.pk})
        response = client.patch(url, {'status_document': magic_numbers.status_statement_sailor_passport_valid})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.statement_sailor_passport.refresh_from_db()
        self.assertEqual(self.statement_sailor_passport.status_document.id,
                         magic_numbers.status_statement_sailor_passport_in_process)
        self.sailor_passport.refresh_from_db()
        self.assertEqual(self.sailor_passport.date_renewal, None)

    def test_invalid_update_statement_sailor_passport_v2(self):
        """Заявление не оплачено, меняем статус на Схвалено"""
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:statement-sailor-passport-detail', kwargs={'pk': self.statement_sailor_passport.pk,
                                                                     'sailor_pk': self.sailor_key.pk})
        response = client.patch(url, {'status_document': magic_numbers.status_statement_sailor_passport_valid})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.statement_sailor_passport.refresh_from_db()
        self.assertEqual(self.statement_sailor_passport.status_document.id,
                         magic_numbers.status_statement_sailor_passport_in_process)
        self.sailor_passport.refresh_from_db()
        self.assertEqual(self.sailor_passport.date_renewal, None)

    def test_valid_update_statement_sailor_passport(self):
        """Заявление оплачиваем и меняем статус на Схвалено"""
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        date_renewal = self.sailor_passport.date_end + relativedelta(years=5)
        url = reverse('v1:statement-sailor-passport-detail', kwargs={'pk': self.statement_sailor_passport.pk})
        response = client.patch(url, {'status_document': magic_numbers.status_statement_sailor_passport_valid,
                                      'is_payed': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.statement_sailor_passport.refresh_from_db()
        self.assertEqual(self.statement_sailor_passport.status_document.id,
                         magic_numbers.status_statement_sailor_passport_valid)
        self.sailor_passport.refresh_from_db()
        self.assertEqual(self.sailor_passport.date_renewal, date_renewal)

    def test_valid_update_statement_sailor_passport_v2(self):
        """Заявление оплачиваем и меняем статус на Схвалено"""
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        date_renewal = self.sailor_passport.date_end + relativedelta(years=5)
        url = reverse('v2:statement-sailor-passport-detail', kwargs={'pk': self.statement_sailor_passport.pk,
                                                                     'sailor_pk': self.sailor_key.pk})
        response = client.patch(url, {'status_document': magic_numbers.status_statement_sailor_passport_valid,
                                      'is_payed': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.statement_sailor_passport.refresh_from_db()
        self.assertEqual(self.statement_sailor_passport.status_document.id,
                         magic_numbers.status_statement_sailor_passport_valid)
        self.sailor_passport.refresh_from_db()
        self.assertEqual(self.sailor_passport.date_renewal, date_renewal)


class UpdateApproveStatementSailorPassportViewsetTest(TestCase):
    """Обновление заявления на ПОМ, создание ПОМ"""
    databases = '__all__'
    fixtures = ['directory_fixture.json', 'agent_groups.json', 'user_profile.json', 'users.json',
                'status_document_statement_sailor_passport.json']

    def setUp(self) -> None:
        self.sailor_key = SailorKeys.objects.create(profile=0)
        user = User.objects.create_user(username='testuser', email='testuser@test.com',
                                        password='testing', is_superuser=True)
        self.statement_sailor_passport = StatementSailorPassport.objects.create(
            number=1,
            port_id=1,
            is_payed=False,
            is_continue=False,
            status_document_id=magic_numbers.status_statement_sailor_passport_in_process,
            sailor_passport=None,
            type_receipt=2,
        )
        self.sailor_key.statement_sailor_passport.append(self.statement_sailor_passport.pk)
        self.sailor_key.save(update_fields=['statement_sailor_passport'])
        self.token, _ = Token.objects.get_or_create(user=user)

    def test_invalid_update_statement_not_paid(self):
        """Заявление не оплачено, меняем статус на Схвалено"""
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:statement-sailor-passport-detail', kwargs={'pk': self.statement_sailor_passport.pk})
        response = client.patch(url, {'status_document': magic_numbers.status_statement_sailor_passport_valid,
                                      'number_document': 10})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.statement_sailor_passport.refresh_from_db()
        self.assertEqual(self.statement_sailor_passport.status_document.id,
                         magic_numbers.status_statement_sailor_passport_in_process)
        self.assertEqual(SailorPassport.objects.count(), 0)

    def test_invalid_update_statement_not_paid_v2(self):
        """Заявление не оплачено, меняем статус на Схвалено"""
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:statement-sailor-passport-detail', kwargs={'pk': self.statement_sailor_passport.pk,
                                                                     'sailor_pk': self.sailor_key.pk})
        response = client.patch(url, {'status_document': magic_numbers.status_statement_sailor_passport_valid,
                                      'number_document': 10})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.statement_sailor_passport.refresh_from_db()
        self.assertEqual(self.statement_sailor_passport.status_document.id,
                         magic_numbers.status_statement_sailor_passport_in_process)
        self.assertEqual(SailorPassport.objects.count(), 0)

    def test_invalid_update_statement_not_number_document(self):
        """Заявление оплачено, меняем статус на Схвалено, не указан номер новой ПОМ"""
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:statement-sailor-passport-detail', kwargs={'pk': self.statement_sailor_passport.pk})
        response = client.patch(url, {'status_document': magic_numbers.status_statement_sailor_passport_valid,
                                      'is_payed': True})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.statement_sailor_passport.refresh_from_db()
        self.assertEqual(self.statement_sailor_passport.status_document.id,
                         magic_numbers.status_statement_sailor_passport_in_process)
        self.assertEqual(SailorPassport.objects.count(), 0)

    def test_invalid_update_statement_not_number_document_v2(self):
        """Заявление оплачено, меняем статус на Схвалено, не указан номер новой ПОМ"""
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:statement-sailor-passport-detail', kwargs={'pk': self.statement_sailor_passport.pk,
                                                                     'sailor_pk': self.sailor_key.pk})
        response = client.patch(url, {'status_document': magic_numbers.status_statement_sailor_passport_valid,
                                      'is_payed': True})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.statement_sailor_passport.refresh_from_db()
        self.assertEqual(self.statement_sailor_passport.status_document.id,
                         magic_numbers.status_statement_sailor_passport_in_process)
        self.assertEqual(SailorPassport.objects.count(), 0)

    def test_valid_update_statement_sailor_passport(self):
        """Заявление оплачиваем, меняем статус на Схвалено и указываем номер новой ПОМ"""
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:statement-sailor-passport-detail', kwargs={'pk': self.statement_sailor_passport.pk})
        response = client.patch(url, {'status_document': magic_numbers.status_statement_sailor_passport_valid,
                                      'is_payed': True, 'number_document': 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.statement_sailor_passport.refresh_from_db()
        self.assertEqual(self.statement_sailor_passport.status_document.id,
                         magic_numbers.status_statement_sailor_passport_valid)
        self.sailor_key.refresh_from_db()
        self.assertIsInstance(self.statement_sailor_passport.sailor_passport, SailorPassport)
        self.assertEqual(SailorPassport.objects.count(), 1)
        self.assertEqual(len(self.sailor_key.sailor_passport), 1)
        sailor_passport = SailorPassport.objects.get(id=self.sailor_key.sailor_passport[0])
        self.assertEqual(int(sailor_passport.number_document), 10)

    def test_valid_update_statement_sailor_passport_v2(self):
        """Заявление оплачиваем, меняем статус на Схвалено и указываем номер новой ПОМ"""
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v2:statement-sailor-passport-detail', kwargs={'pk': self.statement_sailor_passport.pk,
                                                                     'sailor_pk': self.sailor_key.pk})
        response = client.patch(url, {'status_document': magic_numbers.status_statement_sailor_passport_valid,
                                      'is_payed': True, 'number_document': 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.statement_sailor_passport.refresh_from_db()
        self.assertEqual(self.statement_sailor_passport.status_document.id,
                         magic_numbers.status_statement_sailor_passport_valid)
        self.sailor_key.refresh_from_db()
        self.assertIsInstance(self.statement_sailor_passport.sailor_passport, SailorPassport)
        self.assertEqual(SailorPassport.objects.count(), 1)
        self.assertEqual(len(self.sailor_key.sailor_passport), 1)
        sailor_passport = SailorPassport.objects.get(id=self.sailor_key.sailor_passport[0])
        self.assertEqual(int(sailor_passport.number_document), 10)
