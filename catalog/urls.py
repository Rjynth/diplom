from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ShopViewSet,
    CategoryViewSet,
    ProductViewSet,
    ProductInfoViewSet,
    ParameterViewSet,
    ProductParameterViewSet,
    ProductListAPIView,
    ProductDetailAPIView
)

router = DefaultRouter()
router.register(r'shops', ShopViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'product-info', ProductInfoViewSet)
router.register(r'parameters', ParameterViewSet)
router.register(r'product-parameters', ProductParameterViewSet)

urlpatterns = [
    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('api/', include(router.urls)),
    path('products/<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
]
