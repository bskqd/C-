import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory

import user_profile.models
from user_profile.views import SomeDataAPI

User = get_user_model()

client = APIClient()
factory_client = APIRequestFactory()


class CreateAgentProfile(TestCase):
    databases = '__all__'
    fixtures = ['directory_fixture.json', 'agent_groups.json', 'user_profile.json', 'users.json', ]

    def setUp(self) -> None:
        user = User.objects.create_user(username='testuser', email='testuser@test.com',
                                        password='testing', is_superuser=True)
        self.token, _ = Token.objects.get_or_create(user=user)

        load_perms = SomeDataAPI()
        load_perms.load_perms()

    def test_create_agent_profile(self):
        """проверка создания агента из АС c загрузкой фото"""
        client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('v1:users-list')
        main_group = user_profile.models.MainGroups.objects.get(name='Довірена особа')
        response = client.post(url, data={'first_name': 'test', 'last_name': 'test', 'password': 'test',
                                          'username': 'tefffffst', 'is_active': True,
                                          'userprofile': {
                                              'additional_data': '', 'branch_office': 'Миколаїв',
                                              'city': 'Чернівці', 'middle_name': 'test', 'agent_group': [1],
                                              'main_group': [main_group.name], 'contact_info': [{
                                                  'type_contact': 'phone_number',
                                                  'value': '+380950000000'
                                              }]
                                          }
                                          })
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username__exact='tefffffst')
        self.assertEqual(user.userprofile.type_user, 'agent')
        self.assertEqual(bool(user.userprofile.photo), False)
        image = Image.new('RGB', (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file)
        with open(tmp_file.name, 'rb') as data:
            response = client.post(reverse('v1:users-upload-agent-photo'), data={'user': user.pk,
                                                                                 'photo': data}, format='multipart')
            print(response.data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            user.userprofile.refresh_from_db()
            self.assertEqual(bool(user.userprofile.photo), True)
