from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .serializers import RegisterSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

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
        send_mail(
            subject=f'Добро пожаловать, {user.get_full_name() or user.email}!',
            message='Спасибо за регистрацию на нашем сервисе. Теперь вы можете добавлять товары в корзину и подтверждать заказы.',
            from_email='no-reply@yourshop.com',
            recipient_list=[user.email],
            fail_silently=True,
        )


        # 4) Формируем ответ
        data = {
            'user': RegisterSerializer(user).data,
            **tokens
        }
        return Response(data, status=status.HTTP_201_CREATED)
