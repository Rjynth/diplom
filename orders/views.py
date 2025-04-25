from django.shortcuts import render

from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail
from .models import Cart, CartItem, Contact, Order, OrderItem
from .serializers import CartSerializer, CartItemSerializer, ContactSerializer, OrderConfirmSerializer, OrderSerializer, \
    OrderListSerializer, OrderDetailSerializer, OrderStatusSerializer


class CartRetrieveAPIView(generics.RetrieveAPIView):
    """
    GET  /api/cart/     — возвращает корзину текущего пользователя.
    """
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Получаем или создаём корзину для текущего пользователя
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart


class CartItemCreateAPIView(generics.CreateAPIView):
    """
    POST /api/cart/items/ — добавляет товар в корзину (или создаёт новую позицию).
    """
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Автоматически привязываем позицию к корзине текущего пользователя
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)


class CartItemDestroyAPIView(generics.DestroyAPIView):
    """
    DELETE /api/cart/items/{pk}/ — удаляет позицию из корзины.
    """
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        # Разрешаем удалять только свои позиции
        return CartItem.objects.filter(cart__user=self.request.user)




class ContactListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/contacts/    — список контактов текущего пользователя.
    POST /api/contacts/    — создать новый контакт (телефон или адрес).
    """
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Возвращаем только свои контакты
        return Contact.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Привязываем контакт к request.user
        serializer.save(user=self.request.user)


class ContactDestroyAPIView(generics.DestroyAPIView):
    """
    DELETE /api/contacts/{pk}/  — удалить свой контакт по его pk.
    """
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        # Можно удалять только свои контакты
        return Contact.objects.filter(user=self.request.user)



class OrderConfirmAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # 1) Сериализуем и валидация contact_id
        serializer = OrderConfirmSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        contact = serializer.validated_data['contact']

        # 2) Берём корзину пользователя
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = cart.items.select_related('product_info__shop')
        if not items.exists():
            return Response({"detail": "Корзина пуста."}, status=status.HTTP_400_BAD_REQUEST)

        # 3) Создаём заказ
        order = Order.objects.create(
            user=request.user,
            contact=contact,
            status=Order.STATUS_NEW
        )

        # 4) Переносим позиции
        order_items = []
        for ci in items:
            order_items.append(OrderItem(
                order=order,
                product_info=ci.product_info,
                shop=ci.product_info.shop,
                quantity=ci.quantity,
                price=ci.product_info.price
            ))
        OrderItem.objects.bulk_create(order_items)

        # 5) Очищаем корзину
        items.delete()

        # 6) Отправляем email (синхронно)
        subject = f'Ваш заказ #{order.pk} подтверждён'
        message = (
            f'Здравствуйте, {request.user.get_full_name() or request.user.email}!\n\n'
            f'Ваш заказ #{order.pk} успешно создан.\n'
            f'Сумма заказа: {order.total_sum:.2f}.\n'
            f'Статус: {order.get_status_display()}.\n\n'
            'Спасибо за покупку!'
        )
        send_mail(subject, message, 'no-reply@yourshop.com', [request.user.email])

        # 7) Возвращаем готовый заказ
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderListAPIView(generics.ListAPIView):
    """
    GET /api/orders/ — возвращает список заказов текущего пользователя
    в формате: {id, dt, total_sum, status}.
    """
    serializer_class   = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # отдаём только свои заказы, сортируя по дате — самые свежие первыми
        return Order.objects.filter(user=self.request.user).order_by('-dt')



class OrderDetailAPIView(generics.RetrieveAPIView):
    """
    GET /api/orders/{pk}/ — детали заказа вместе с позициями и контактами.
    """
    serializer_class   = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Пользователь может смотреть только свои заказы
        return Order.objects.filter(user=self.request.user)


class OrderStatusUpdateAPIView(generics.UpdateAPIView):
    """
    PATCH /api/orders/{pk}/status/ — изменить статус заказа (для staff).
    """
    serializer_class   = OrderStatusSerializer
    permission_classes = [permissions.IsAdminUser]  # или IsAuthenticated & user.is_staff

    lookup_url_kwarg   = 'pk'
    lookup_field       = 'pk'

    def get_queryset(self):
        # Только staff/admin может менять статус любых заказов
        return Order.objects.all()