from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class RegisterLoginViewTests(APITestCase):
    def test_register_and_receive_tokens(self):
        url = reverse('register')
        payload = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test.user@example.com",
            "password": "Password123"
        }
        resp = self.client.post(url, data=payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)

    def test_login_with_wrong_credentials(self):
        url = reverse('token_obtain_pair')
        # не существующий пользователь
        resp = self.client.post(url, data={"username": "noone", "password": "bad"}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)