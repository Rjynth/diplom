from django.urls import path
from .views import OrderConfirmAPIView, OrderListAPIView, OrderConfirmAPIView, OrderDetailAPIView, OrderStatusUpdateAPIView

urlpatterns = [
    path('confirm/', OrderConfirmAPIView.as_view(), name='order-confirm'),
    path('', OrderListAPIView.as_view(), name='order-list'),
    path('confirm/', OrderConfirmAPIView.as_view(), name='order-confirm'),
    path('<int:pk>/', OrderDetailAPIView.as_view(), name='order-detail'),
    path('<int:pk>/status/', OrderStatusUpdateAPIView.as_view(), name='order-status'),
]
