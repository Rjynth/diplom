from rest_framework import serializers
from .models import (
    Shop, Category, Product,
    ProductInfo, Parameter, ProductParameter
)

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Shop
        fields = ['id', 'name', 'url']


class CategorySerializer(serializers.ModelSerializer):
    # при выводе — вложенные объекты магазинов
    shops     = ShopSerializer(many=True, read_only=True)
    # при записи — список PK магазинов
    shops_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Shop.objects.all(),
        source='shops',
        write_only=True
    )

    class Meta:
        model  = Category
        fields = [
            'id', 'name', 'slug', 'description',
            'shops', 'shops_ids'
        ]
        read_only_fields = ['slug']


class ProductSerializer(serializers.ModelSerializer):
    # вложенная категория при GET
    category     = CategorySerializer(read_only=True)
    # при POST/PUT приходят только ID
    category_id  = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model  = Product
        fields = ['id', 'name', 'category', 'category_id']


class ProductInfoSerializer(serializers.ModelSerializer):
    # вложенные «родительские» объекты
    product     = ProductSerializer(read_only=True)
    shop        = ShopSerializer(read_only=True)
    # для записи через API — их PK
    product_id  = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    shop_id     = serializers.PrimaryKeyRelatedField(
        queryset=Shop.objects.all(),
        source='shop',
        write_only=True
    )

    class Meta:
        model  = ProductInfo
        fields = [
            'id', 'product', 'product_id',
            'shop', 'shop_id',
            'name', 'quantity', 'price', 'price_rrc',
        ]
        # все цены и количество можно менять,
        # SKU у вас в модели генерируется автоматически, здесь нет


class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Parameter
        fields = ['id', 'name']


class ProductParameterSerializer(serializers.ModelSerializer):
    # вложенный ProductInfo + Parameter
    product_info    = ProductInfoSerializer(read_only=True)
    parameter       = ParameterSerializer(read_only=True)
    # и их PK для записи
    product_info_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductInfo.objects.all(),
        source='product_info',
        write_only=True
    )
    parameter_id    = serializers.PrimaryKeyRelatedField(
        queryset=Parameter.objects.all(),
        source='parameter',
        write_only=True
    )

    class Meta:
        model  = ProductParameter
        fields = [
            'id',
            'product_info', 'product_info_id',
            'parameter',    'parameter_id',
            'value'
        ]


class ProductItemSerializer(serializers.ModelSerializer):
    external_id     = serializers.IntegerField(source='product.external_id', read_only=True)
    name            = serializers.CharField(source='product.name',        read_only=True)
    description     = serializers.CharField(source='product.description', read_only=True, default='')
    supplier        = ShopSerializer(source='shop',                        read_only=True)
    characteristics = serializers.SerializerMethodField()
    price           = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    price_rrc       = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    quantity        = serializers.IntegerField(read_only=True)

    class Meta:
        model  = ProductInfo
        fields = [
            'id',
            'external_id',
            'name',
            'description',
            'supplier',
            'characteristics',
            'price',
            'price_rrc',
            'quantity',
        ]

    def get_characteristics(self, obj):
        return {
            pp.parameter.name: pp.value
            for pp in obj.productparameter_set.all()
        }