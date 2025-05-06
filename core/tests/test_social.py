from django.urls import reverse
from rest_framework.test import APITestCase, override_settings
from rest_framework import status
from unittest.mock import patch

@override_settings(
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY='test',
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET='test',
)
class SocialAuthTests(APITestCase):
    @patch('core.views.request')
    def test_google_social_login(self, mock_request):
        # Мокаем PSA-do_auth, чтобы не обращаться к реальному Google
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(email='g@example.com', password='pwd12345')

        class DummyBackend:
            name = 'google-oauth2'
            def do_auth(self, token, *args, **kwargs):
                return user

        mock_request.backend = DummyBackend()
        url = reverse('social-login', args=['google-oauth2'])
        resp = self.client.post(url, data={'access_token': 'fake'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)
