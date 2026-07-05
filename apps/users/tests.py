from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import User, StudentProfile


class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/v1/auth/register/'
        self.login_url = '/api/v1/auth/login/'

    def test_register_creates_user_and_profile(self):
        response = self.client.post(self.register_url, {
            'email': 'test@example.com',
            'password': 'testpass123',
            'full_name': 'Test User',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='test@example.com').exists())
        user = User.objects.get(email='test@example.com')
        self.assertTrue(StudentProfile.objects.filter(user=user).exists())

    def test_login_returns_tokens(self):
        User.objects.create_user(email='test@example.com', password='testpass123', full_name='Test')
        response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials_returns_401(self):
        response = self.client.post(self.login_url, {
            'email': 'nobody@example.com',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_duplicate_email_registration_fails(self):
        User.objects.create_user(email='test@example.com', password='testpass123', full_name='Test')
        response = self.client.post(self.register_url, {
            'email': 'test@example.com',
            'password': 'anotherpass123',
            'full_name': 'Another User',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
