from django.urls import path
from .views import (
    CartRetrieveAPIView,
    CartItemCreateAPIView,
    CartItemDestroyAPIView,
)

urlpatterns = [
    path('',            CartRetrieveAPIView.as_view(),      name='cart-detail'),
    path('items/',      CartItemCreateAPIView.as_view(),   name='cartitem-create'),
    path('items/<int:pk>/', CartItemDestroyAPIView.as_view(), name='cartitem-delete'),
]
