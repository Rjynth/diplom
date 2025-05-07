from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from catalog.models import Shop, Category, Product, ProductInfo

class CatalogViewTests(APITestCase):
    def setUp(self):
        shop = Shop.objects.create(name='S', url='https://s.example')
        cat  = Category.objects.create(name='C', slug='c')
        cat.shops.add(shop)
        prod = Product.objects.create(name='P', category=cat)
        self.pi = ProductInfo.objects.create(
            product=prod, shop=shop,
            name='P-info', quantity=5,
            price=10.00, price_rrc=12.00
        )

    def test_product_list(self):
        url = reverse('product-list')
        resp = self.client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # без пагинации вернётся список
        self.assertTrue(isinstance(resp.data, list))
        self.assertGreaterEqual(len(resp.data), 1)

    def test_product_detail(self):
        url = reverse('product-detail', args=[self.pi.id])
        resp = self.client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['id'], self.pi.id)
        self.assertIn('characteristics', resp.data)