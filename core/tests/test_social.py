from django.urls import reverse
from rest_framework.test import APITestCase, override_settings
from rest_framework import status
from unittest.mock import patch
from django.contrib.auth import get_user_model

@override_settings(
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY='test',
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET='test',
)
class SocialAuthTests(APITestCase):
    def test_google_social_login(self):
        """
        Проверяем, что при корректном возвращении пользователя из GoogleOAuth2 мы
        отдаем валидные JWT-токены.
        """
        # 1) Создаём пользователя, которого будет возвращать do_auth
        User = get_user_model()
        user = User.objects.create_user(
            username='guser',
            email='g@example.com',
            password='pwd12345'
        )

        # 2) Подготавливаем URL и мокируем оба метода в контексте
        from social_core.backends.google import GoogleOAuth2
        url = reverse('social-login', args=['google-oauth2'])
        with patch.object(GoogleOAuth2, 'user_data', return_value={'sub': '123', 'email': 'g@example.com'}), \
             patch.object(GoogleOAuth2, 'do_auth', return_value=user):
            resp = self.client.post(
                url,
                data={'access_token': 'fake-token'},
                format='json'
            )
            # 3) Успешный ответ с JWT
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            self.assertIn('access', resp.data)
            self.assertIn('refresh', resp.data)

        # При повторном запросе поведение то же самое
        with patch.object(GoogleOAuth2, 'user_data', return_value={'sub': '123', 'email': 'g@example.com'}), \
             patch.object(GoogleOAuth2, 'do_auth', return_value=user):
            resp2 = self.client.post(
                url,
                data={'access_token': 'fake-token'},
                format='json'
            )
            self.assertEqual(resp2.status_code, status.HTTP_200_OK)
            self.assertIn('access', resp2.data)
            self.assertIn('refresh', resp2.data)
