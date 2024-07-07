from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import CustomUser, Organisation

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
        