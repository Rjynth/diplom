"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularSwaggerView
)
from core.views import RegisterAPIView, LoginAPIView, RefreshAPIView, SocialLoginAPIView, TokenObtainPairView






urlpatterns = [
    path('baton/', include('baton.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('catalog.urls')),
    path('api/auth/register/',
         RegisterAPIView.as_view(),
         name='register'),
    path('api/auth/login/',
         TokenObtainPairView.as_view(throttle_classes=[]),
         name='token_obtain_pair'),

#   path('api/auth/register/', RegisterAPIView.as_view(), name='register'),
#  path('api/auth/login/', LoginAPIView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/',
         TokenRefreshView.as_view(throttle_classes=[]),
         name='token_refresh'),
    path('api/cart/', include('orders.cart_urls')),
    path('api/contacts/', include('orders.contact_urls')),
    path('api/orders/', include('orders.order_urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(
        url_name='schema'
    ), name='swagger-ui'),
    path('auth/social/', include('social_django.urls', namespace='social')),
#    path('api/auth/social/<str:backend>/', SocialLoginAPIView.as_view(), name='social-login'),
    path('api/auth/social/<str:backend>/',
         SocialLoginAPIView.as_view(throttle_classes=[]),
         name='social-login'),

]