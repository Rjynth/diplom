from django.contrib.auth import get_user_model
from rest_framework import serializers
from catalog.models import Shop, ProductInfo
from .models import Order, OrderItem, Contact
from catalog.serializers import ProductInfoSerializer, ShopSerializer
from django.core.exceptions import ValidationError
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
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )

    class Meta:
        model = Contact
        fields = [
            'id', 'user', 'user_id',
            'type', 'value', 'address',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        contact = Contact(**attrs)
        try:
            contact.full_clean()
        except ValidationError as e:
            # Если e.message_dict есть — отдадим его,
            # иначе — просто список сообщений
            errors = getattr(e, 'message_dict', None) or e.messages
            raise serializers.ValidationError(errors)
        return attrs

