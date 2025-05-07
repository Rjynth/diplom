from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, override_settings
from rest_framework import status
from social_core.backends.google import GoogleOAuth2
from unittest.mock import patch

@override_settings(
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY='test',
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET='test',
)
class SocialAuthTests(APITestCase):
    def test_google_social_login(self):
        # 1) Создаём пользователя, которого вернёт do_auth
        User = get_user_model()
        user = User.objects.create_user(email='g@example.com', password='pwd12345')

        # 2) Формируем URL и данные
        url = reverse('social-login', kwargs={'backend': 'google-oauth2'})
        data = {'access_token': 'fake-token'}

        # 3) Мокаем do_auth у GoogleOAuth2, чтобы возвращался наш user
        with patch.object(GoogleOAuth2, 'do_auth', return_value=user):
            resp = self.client.post(url, data, format='json')

        # 4) Проверяем, что получили OK и оба токена
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access',  resp.data)
        self.assertIn('refresh', resp.data)