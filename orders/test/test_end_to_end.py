from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from catalog.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter
from catalog.views import ProductListAPIView

from orders.models import Cart, CartItem, Contact, Order, OrderItem
from orders.views import OrderListAPIView

# Отключаем пагинацию на уровне view только в контексте тестов
ProductListAPIView.pagination_class = None
OrderListAPIView.pagination_class   = None

User = get_user_model()

@override_settings(REST_FRAMEWORK={'DEFAULT_PAGINATION_CLASS': None})
class EndToEndTests(APITestCase):
    def setUp(self):
        # 1) Создадим каталог: магазин, категорию, товар и ProductInfo + параметры
        self.shop = Shop.objects.create(name='TestShop', url='https://test.shop')
        self.cat  = Category.objects.create(name='TestCat', slug='testcat')
        self.cat.shops.add(self.shop)
        self.prod = Product.objects.create(name='TestProd', category=self.cat, external_id=100)
        self.pi   = ProductInfo.objects.create(
            product=self.prod, shop=self.shop,
            name='TestProd Info', quantity=10,
            price=123.45, price_rrc=150.00
        )
        # параметр
        param = Parameter.objects.create(name='Color')
        ProductParameter.objects.create(product_info=self.pi, parameter=param, value='red')

        # URL’ы
        self.register_url = reverse('register')
        self.login_url    = reverse('token_obtain_pair')
        self.refresh_url  = reverse('token_refresh')
        self.products_url = reverse('product-list')
        self.product_detail_url = lambda pk: reverse('product-detail', args=[pk])
        self.cart_url     = reverse('cart-detail')
        self.cart_items_url = reverse('cartitem-create')
        self.contacts_url = reverse('contact-list-create')
        self.order_confirm_url = reverse('order-confirm')
        self.order_list_url    = reverse('order-list')
        self.order_detail_url  = lambda pk: reverse('order-detail', args=[pk])
        self.order_status_url  = lambda pk: reverse('order-status', args=[pk])

        # Данные пользователей
        self.user_data = {
            'first_name': 'Ivan',
            'last_name': 'Test',
            'email': 'ivan@test.com',
            'password': 'StrongPass123'
        }
        # создадим ещё staff-пользователя для смены статуса
        self.staff = User.objects.create_user(
            username='staff', email='staff@test.com', password='StaffPass123'
        )
        self.staff.is_staff = True
        self.staff.save()

    def test_full_scenario(self):
        # 1) Регистрация
        resp = self.client.post(self.register_url, data=self.user_data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # убедимся, что получили токены
        access = resp.data['access']
        refresh = resp.data['refresh']

        # 2) Логин (проверим refresh)
        resp2 = self.client.post(self.refresh_url, data={'refresh': refresh}, format='json')
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        access = resp2.data['access']

        # 3) Список товаров и детали
        resp = self.client.get(self.products_url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # вместо resp.data[0] будем извлекать корректный массив
        products = resp.data if isinstance(resp.data, list) else resp.data.get('results', [])
        self.assertTrue(len(products) >= 1)
        item = products[0]

        resp = self.client.get(self.product_detail_url(item['id']), format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('characteristics', resp.data)

        # 4) Корзина пуста
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        resp = self.client.get(self.cart_url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['items'], [])

        # 5) Добавляем товар в корзину
        resp = self.client.post(self.cart_items_url,
                                data={'product_info_id': self.pi.id, 'quantity': 2},
                                format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # проверяем наличие
        resp = self.client.get(self.cart_url, format='json')
        self.assertEqual(len(resp.data['items']), 1)

        # 6) Добавляем контакты
        resp = self.client.post(self.contacts_url,
                                data={'type': 'PHONE', 'value': '+70000000000'},
                                format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp = self.client.post(self.contacts_url,
                                data={'type': 'ADDRESS', 'address': {
                                    'city':'M','street':'S','house':'1'}},
                                format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # запомним контакт для заказа
        resp = self.client.get(self.contacts_url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Распаковываем список контактов из пагинированного ответа
        contacts = (
            resp.data
            if isinstance(resp.data, list)
            else resp.data.get('results', [])
        )
        self.assertTrue(len(contacts) >= 2)
        contact_id = contacts[1]['id']

        # 7) Подтверждение заказа
        resp = self.client.post(self.order_confirm_url,
                                data={'contact_id': contact_id}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        order_id = resp.data['id']

        # 8) Список заказов
        resp = self.client.get(self.order_list_url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        orders = resp.data if isinstance(resp.data, list) else resp.data.get('results', [])
        self.assertTrue(any(o['id'] == order_id for o in orders))

        # 9) Детали заказа
        resp = self.client.get(self.order_detail_url(order_id), format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('items', resp.data)
        self.assertIn('contact', resp.data)

        # 10) Смена статуса (от лица staff)
        # логинимся как staff
        resp = self.client.post(
            self.login_url,
            data={'username': 'staff', 'password': 'StaffPass123'},
            format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        staff_token = resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {staff_token}')
        # патчим статус
        resp = self.client.patch(self.order_status_url(order_id),
                                 data={'status': Order.STATUS_SHIPPED}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['status'], Order.STATUS_SHIPPED)
