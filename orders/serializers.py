from django.contrib.auth import get_user_model
from rest_framework import serializers
from catalog.models import Shop, ProductInfo
from .models import Order, OrderItem, Contact, Cart, CartItem
from catalog.serializers import ProductInfoSerializer, ShopSerializer
from django.core.exceptions import ValidationError as DjangoValidationError

User = get_user_model()


class OrderItemSerializer(serializers.ModelSerializer):
    """Сериализатор для позиций заказа."""
    product_info = ProductInfoSerializer(read_only=True)
    shop = ShopSerializer(read_only=True)
    product_info_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductInfo.objects.all(),
        source='product_info',
        write_only=True
    )
    shop_id = serializers.PrimaryKeyRelatedField(
        queryset=Shop.objects.all(),
        source='shop',
        write_only=True
    )
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(),
        source='order',
        write_only=True,
        required=False
    )

    class Meta:
        model = OrderItem
        fields = [
            'id', 'order_id',
            'product_info', 'product_info_id',
            'shop', 'shop_id',
            'quantity', 'price',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        prod_info = attrs.get('product_info') or getattr(self.instance, 'product_info', None)
        shop      = attrs.get('shop')        or getattr(self.instance, 'shop', None)
        if prod_info and shop and prod_info.shop != shop:
            raise serializers.ValidationError(
                "Магазин в OrderItem должен совпадать с shop из product_info."
            )
        return attrs


class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор для заказа."""
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_id',
            'dt', 'status',
            'items',
        ]
        read_only_fields = ['id', 'dt']


class ContactSerializer(serializers.ModelSerializer):
    """Сериализатор для контактных данных пользователя."""
    user = serializers.StringRelatedField(read_only=True)


    class Meta:
        model = Contact
        fields = [
            'id', 'user', 'user_id',
            'type', 'value', 'address',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        # Создаём временный объект с user из контекста
        user = self.context['request'].user
        contact = Contact(user=user, **attrs)

        # Вызываем модельную валидацию
        try:
            contact.full_clean()
        except DjangoValidationError as e:
            # Преобразуем ошибки модели в ошибки сериализатора
            raise serializers.ValidationError(
                getattr(e, 'message_dict', e.messages)
            )
        return attrs




class CartItemSerializer(serializers.ModelSerializer):
    """Сериализатор для элементов корзины."""
    # вложенный продукт для чтения
    product_info = ProductInfoSerializer(read_only=True)
    # для записи принимаем только PK
    product_info_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductInfo.objects.all(),
        source='product_info',
        write_only=True
    )


    class Meta:
        model = CartItem
        fields = ['id', 'product_info', 'product_info_id', 'quantity']
        read_only_fields = ['id']

    def create(self, validated_data):
        # сюда попадает 'cart' из perform_create и 'product_info', 'quantity'
        cart = validated_data['cart']
        product_info = validated_data['product_info']
        quantity = validated_data['quantity']

        # пытаемся найти существующую позицию
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_info=product_info,
            defaults={'quantity': quantity}
        )
        if not created:
            # обновляем количество
            cart_item.quantity += quantity
            cart_item.save()
        return cart_item


class CartSerializer(serializers.ModelSerializer):
    """Сериализатор для корзины и её элементов."""
    # вложенные элементы корзины
    items = CartItemSerializer(many=True, read_only=True)
    # юзер для чтения
    user = serializers.StringRelatedField(read_only=True)
    # для записи через API (если нужно создавать корзину вручную)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )

    class Meta:
        model = Cart
        fields = [
            'id',
            'user', 'user_id',
            'created_dt', 'updated_dt',
            'items',
        ]
        read_only_fields = ['id', 'created_dt', 'updated_dt']


class OrderConfirmSerializer(serializers.Serializer):
    contact_id = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all(),
        source='contact',
        write_only=True
    )

    def validate_contact(self, contact):
        user = self.context['request'].user
        if contact.user != user:
            raise serializers.ValidationError("Контакт не принадлежит текущему пользователю.")
        return contact





class OrderListSerializer(serializers.ModelSerializer):
    total_sum = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Order
        fields = ['id', 'dt', 'total_sum', 'status']



class OrderDetailSerializer(serializers.ModelSerializer):
    items     = OrderItemSerializer(many=True, read_only=True)
    total_sum = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    contact   = ContactSerializer(read_only=True)

    class Meta:
        model  = Order
        fields = [
            'id', 'dt', 'status', 'total_sum',
            'contact', 'items',
        ]


class OrderStatusSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(
        choices=Order.STATUS_CHOICES
    )

    class Meta:
        model  = Order
        fields = ['status']