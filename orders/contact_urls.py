from django.urls import path
from .views import ContactListCreateAPIView, ContactDestroyAPIView

urlpatterns = [
    path('',      ContactListCreateAPIView.as_view(),   name='contact-list-create'),
    path('<int:pk>/', ContactDestroyAPIView.as_view(), name='contact-destroy'),
]