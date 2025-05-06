from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class ThrottlingTests(APITestCase):
    def setUp(self):
        # создаём пользователя и получаем JWT
        self.user = User.objects.create_user(
            username='throttle', email='t@example.com', password='pwd12345'
        )
        # получаем токен
        token_url = reverse('token_obtain_pair')
        resp = self.client.post(token_url, {'username': 'throttle', 'password': 'pwd12345'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.token = resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        # endpoint для теста — например, просмотр каталога
        self.url = reverse('product-list')

    def test_user_rate_throttle(self):
        # 5 запросов должны пройти
        for _ in range(5):
            resp = self.client.get(self.url)
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # 6-й сразу должен вернуть 429
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        # и в теле будет код 429
        self.assertIn('detail', resp.data)
        self.assertIn('Request was throttled', resp.data['detail'])

    def test_anon_rate_throttle(self):
        # сбрасываем авторизацию, чтобы действовали анонимные лимиты
        self.client.credentials()
        for _ in range(2):
            resp = self.client.get(self.url)
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # 3-й запрос анон должен упасть
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
