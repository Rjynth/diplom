from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from core.tasks import send_registration_email
from .serializers import RegisterSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from social_django.utils import psa
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class LoginAPIView(TokenObtainPairView):
    """
    POST /api/auth/login/
    Тело: {"username": "...", "password": "..."}
    Ответ: {"access": "...", "refresh": "..."}
    """
    permission_classes = [AllowAny]
    throttle_classes = []







class RegisterAPIView(APIView):



    """
    POST /api/auth/register/

    Регистрация нового пользователя. На входе:
      - first_name: строка, имя пользователя
      - last_name: строка, фамилия пользователя
      - email: строка, email (должен быть уникальным)
      - password: строка, пароль (минимум 8 символов)

    Возвращает:
      - user: созданный пользователь
      - access, refresh: JWT-токены
    """
    permission_classes = [AllowAny]
    throttle_classes = []
    def post(self, request):
        # 1) Сериализуем и создаём пользователя
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 2) Генерируем для него пару токенов (username_field в JWT по умолчанию — email)
        token_serializer = TokenObtainPairSerializer(data={
            'username': user.username,
            'password': request.data['password'],
        })
        token_serializer.is_valid(raise_exception=True)
        tokens = token_serializer.validated_data  # {'access': ..., 'refresh': ...}

        # 3) Отправляем письмо-подтверждение регистрации
        send_registration_email.delay(
            user.email,
            user.get_full_name() or user.email
        )


        # 4) Формируем ответ
        data = {
            'user': RegisterSerializer(user).data,
            **tokens
        }
        return Response(data, status=status.HTTP_201_CREATED)

class SocialLoginAPIView(APIView):
    """
    POST /api/auth/social/<backend>/
    Тело: { "access_token": "<токен соцсети>" }
    Ответ: {"access": "...", "refresh": "..."}
    """
    permission_classes = []
    throttle_classes = []
    @psa('social:complete')
    def post(self, request, backend):
        token = request.data.get('access_token')
        if not token:
            return Response({'error': 'access_token не указан'},
                            status=status.HTTP_400_BAD_REQUEST)

        # request.backend настроит PSA на нужный social backend
        user = request.backend.do_auth(token)
        if not user or not user.is_active:
            return Response({'error': 'не удалось аутентифицировать'}, status=status.HTTP_400_BAD_REQUEST)

        # Генерируем JWT
        refresh = RefreshToken.for_user(user)
        return Response({
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)

class RefreshAPIView(TokenRefreshView):
    throttle_classes = []
