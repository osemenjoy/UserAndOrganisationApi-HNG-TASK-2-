from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from datetime import timedelta, datetime, timezone as dt_timezone
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, Organisation

class TokenTests(APITestCase):
    def test_token_expiry(self):
        user = CustomUser.objects.create_user(
            username='john@example.com',
            email='john@example.com',
            password='password@123',
            firstName='John',
            lastName='Doe',
            phone='1234567890'
        )
        refresh = RefreshToken.for_user(user)
        exp_timestamp = refresh.access_token.payload['exp']
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=dt_timezone.utc)
        current_time = timezone.now()
        self.assertEqual(refresh.access_token.payload['userId'], str(user.userId))
        self.assertTrue(current_time < exp_datetime)

    def test_organisation_data_access(self):
        org1 = Organisation.objects.create(name='Org 1')
        org2 = Organisation.objects.create(name='Org 2')
        user1 = CustomUser.objects.create_user(
            username='john1@example.com',
            email='john1@example.com',
            password='password@123',
            firstName='John1',
            lastName='Doe1',
            phone='1234567891'
        )
        user2 = CustomUser.objects.create_user(
            username='john2@example.com',
            email='john2@example.com',
            password='password@123',
            firstName='John2',
            lastName='Doe2',
            phone='1234567892'
        )
        org1.users.add(user1)
        org2.users.add(user2)
        url = reverse('get_an_organisation', kwargs={'orgId': org2.orgId})
        self.client.force_authenticate(user=user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class AuthTests(APITestCase):
    def test_register_user_successfully(self):
        url = reverse('register')
        data = {
            'username': 'john@example.com',
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john@example.com',
            'password': 'password@123',
            'phone': '1234567890'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(Organisation.objects.count(), 1)
        self.assertEqual(Organisation.objects.first().name, "John's Organisation")

    def test_login_user_successfully(self):
        user = CustomUser.objects.create_user(
            username = 'john@example.com',
            firstName='John',
            lastName='Doe',
            email='john@example.com',
            password='password@123'
        )
        url = reverse('login')
        data = {'email': 'john@example.com', 'password': 'password@123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')

    def test_register_user_missing_fields(self):
        url = reverse('register')
        data = {'firstName': 'John'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_register_duplicate_email(self):
        CustomUser.objects.create_user(
            username = 'john@example.com',
            firstName='John',
            lastName='Doe',
            email='john@example.com',
            password='password@123'
        )
        url = reverse('register')
        data = {
            'firstName': 'Jane',
            'lastName': 'Doe',
            'email': 'john@example.com',
            'password': 'password@123',
            'phone': '1234567890'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
   