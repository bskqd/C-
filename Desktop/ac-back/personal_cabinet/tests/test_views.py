from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APIRequestFactory

from communication.models import SailorKeys
from itcs import magic_numbers
from personal_cabinet.serializers import PersonalSailorStatementDKKSerialize
from sailor.statement.models import StatementSQC
from user_profile.models import UserProfile

User = get_user_model()

client = APIClient()
factory_client = APIRequestFactory()


class DeleteEducationDocumentTest(TestCase):
    databases = '__all__'
    fixtures = ['status_document_cancel_statement.json', 'directory_fixture.json', 'agent_groups.json',
                'user_profile.json', 'users.json']

    def setUp(self) -> None:
        user = User.objects.create_user(username='key_1', email='testuser@test.com',
                                        password='testing', )
        self.sailor_key = SailorKeys.objects.create(profile=0, user_id=user.pk)
        self.statement_sqc = StatementSQC.objects.create(
            number=1,
            sailor=self.sailor_key.pk,
            rank_id=98,
            list_positions=[123],
            status_document_id=42,
            branch_office_id=2,

        )
        self.invalid_statement = StatementSQC.objects.create(
            number=2,
            sailor=self.sailor_key.pk,
            rank_id=98,
            list_positions=[123],
            status_document_id=42,
            branch_office_id=2,

        )
        self.sailor_key.statement_dkk.append(self.statement_sqc.pk)
        self.sailor_key.save(update_fields=['statement_dkk'])
        self.token, _ = Token.objects.get_or_create(user=user)
        secretary = User.objects.create(username='secretary', email='testuser@test.com',
                                        password='testing', )
        UserProfile.objects.create(user=secretary, type_user=UserProfile.SECRETARY_SQC)
        ct = ContentType.objects.get(model='statementsqc')
        secretary.user_permissions.create(name='readApplicationSQC', codename='readApplicationSQC',
                                          content_type=ct)
        self.secretary_token, _ = Token.objects.get_or_create(user=secretary)

    def test_change_status(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:personal-statement-dkk-cancel_document', kwargs={'pk': self.statement_sqc.pk})
        response = client.patch(url)
        print(response.data)
        self.statement_sqc.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.statement_sqc.status_document_id, magic_numbers.status_state_qual_dkk_canceled)
        valid_response = PersonalSailorStatementDKKSerialize(self.statement_sqc).data
        self.assertEqual(response.data, valid_response)

    def test_change_status_to_another_sailor(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:personal-statement-dkk-cancel_document', kwargs={'pk': self.invalid_statement.pk})
        response = client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_check_secretary_hide_statement(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:personal-statement-dkk-cancel_document', kwargs={'pk': self.statement_sqc.pk})
        client.patch(url)
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.secretary_token.key}')
        url = reverse('v1:statement-sqc-sailor-list', kwargs={'pk': self.sailor_key.pk})
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        
    def test_check_personal_cabinet_hide_statement(self):
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:personal-statement-dkk-cancel_document', kwargs={'pk': self.statement_sqc.pk})
        client.patch(url)
        url = reverse('v1:personal-statement-dkk-sailor')
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
