from rest_framework import viewsets, generics
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter
from .serializers import (
    ShopSerializer,
    CategorySerializer,
    ProductSerializer,
    ProductInfoSerializer,
    ParameterSerializer,
    ProductParameterSerializer
)
from rest_framework import generics, permissions
from .models import ProductInfo
from .serializers import ProductItemSerializer
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
class ShopViewSet(viewsets.ModelViewSet):
    """API endpoint for managing shops."""
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """API endpoint for managing categories."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    """API endpoint for managing products."""
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer


class ProductInfoViewSet(viewsets.ModelViewSet):
    """API endpoint for managing product info (shop listings)."""
    queryset = ProductInfo.objects.select_related('product', 'shop').all()
    serializer_class = ProductInfoSerializer


class ParameterViewSet(viewsets.ModelViewSet):
    """API endpoint for managing parameters."""
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer


class ProductParameterViewSet(viewsets.ModelViewSet):
    """API endpoint for managing product parameters."""
    queryset = ProductParameter.objects.select_related('product_info', 'parameter').all()
    serializer_class = ProductParameterSerializer


class ProductListAPIView(generics.ListAPIView):
    queryset = ProductInfo.objects.select_related('product','shop')\
            .prefetch_related('productparameter_set__parameter')
    serializer_class = ProductItemSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    pagination_class = None

class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = ProductInfo.objects.select_related('product','shop')\
            .prefetch_related('productparameter_set__parameter')
    serializer_class = ProductItemSerializer
    permission_classes = [permissions.AllowAny]