from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, override_settings
from rest_framework import status
from unittest.mock import patch

@override_settings(
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY='test',
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET='test',
)
class SocialAuthTests(APITestCase):
    def test_google_social_login(self):
        # 1) Создаём пользователя, которого вернёт do_auth
        User = get_user_model()
        user = User.objects.create_user(
            username='guser',
            email='g@example.com',
            password='pwd12345'
        )

        # 2) Мокаем do_auth у реального GoogleOAuth2-бэкенда
        from social_core.backends.google import GoogleOAuth2
        with patch.object(GoogleOAuth2, 'do_auth', return_value=user):
            url = reverse('social-login', args=['google-oauth2'])
            resp = self.client.post(
                url,
                data={'access_token': 'fake-token'},
                format='json'
            )
            # 3) Успешный ответ с JWT
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            self.assertIn('access', resp.data)
            self.assertIn('refresh', resp.data)

        # 4) Повторный запрос — тот же результат
        resp = self.client.post(
            url,
            data={'access_token': 'fake-token'},
            format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)
