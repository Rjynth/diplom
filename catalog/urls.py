from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ShopViewSet,
    CategoryViewSet,
    ProductViewSet,
    ProductInfoViewSet,
    ParameterViewSet,
    ProductParameterViewSet
)

router = DefaultRouter()
router.register(r'shops', ShopViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'product-info', ProductInfoViewSet)
router.register(r'parameters', ParameterViewSet)
router.register(r'product-parameters', ProductParameterViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
