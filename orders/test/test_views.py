
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model
from catalog.models import Shop, Category, Product, ProductInfo
from orders.models import Cart, CartItem, Contact

User = get_user_model()

class OrderViewTests(APITestCase):
    def setUp(self):
        # создаём пользователя
        self.user = User.objects.create_user(
            username='u',
            email='u@example.com',
            password='pwd12345'
        )
        # получаем JWT и подставляем в заголовки
        login_url = reverse('token_obtain_pair')
        resp = self.client.post(
            login_url,
            data={'username': 'u', 'password': 'pwd12345'},
            format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token = resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # каталог
        shop = Shop.objects.create(name='S', url='https://s.example')
        cat  = Category.objects.create(name='C', slug='c')
        cat.shops.add(shop)
        prod = Product.objects.create(name='P', category=cat)
        self.pi = ProductInfo.objects.create(
            product=prod, shop=shop,
            name='P-info', quantity=5,
            price=10.00, price_rrc=12.00
        )

    def test_cart_add_and_get(self):
        url_add = reverse('cartitem-create')
        resp = self.client.post(url_add, data={'product_info_id': self.pi.id, 'quantity': 2}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        url_get = reverse('cart-detail')
        resp = self.client.get(url_get, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data['items']), 1)

    def test_create_and_list_contact(self):
        url = reverse('contact-list-create')
        # добавляем телефон
        resp = self.client.post(url, data={'type':'PHONE','value':'+7000000000'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # список
        resp = self.client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(resp.data) >= 1)
