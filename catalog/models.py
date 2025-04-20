from django.db import models

from django.db import models
from django.db.models import JSONField, CASCADE
from django.utils.text import slugify
import uuid

class Shop(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField(max_length=200, verbose_name="Ссылка на сайт магазина", unique=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)

    shops = models.ManyToManyField(Shop, blank=True, related_name='categories')

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        indexes = [
            models.Index(fields=['slug']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:190]
            slug = base
            num = 1
            while Category.objects.filter(slug=slug).exists():
                num += 1
                slug = f"{base}-{num}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return f"{self.name} ({self.category.name})"

class ProductInfo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='info')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='product_info')
    name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=200, decimal_places=2)
    price_rrc = models.DecimalField(max_digits=200, decimal_places=2)

    class Meta:
        unique_together = (('product', 'shop'),)
        indexes = [models.Index(fields=['product', 'shop'])]

    def __str__(self):
        return f"{self.shop.name}: {self.name} - {self.price}"

class Parameter(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, on_delete=CASCADE)
    value = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.product_info} | {self.parameter.name}: {self.value}"










#     description = models.TextField(blank=True)
#     characteristics = JSONField(blank=True, default=dict)
#     sku = models.CharField(
#         max_length=32, unique=True, editable=False,
#         help_text="Уникальный артикул (UUID без дефисов)"
#     )
#     price = models.DecimalField(max_digits=12, decimal_places=2)

#     supplier = models.ForeignKey(
#         Supplier, on_delete=models.CASCADE, related_name='products'
#     )
#     stock = models.PositiveIntegerField()
#
#     class Meta:
#         verbose_name = "Товар"
#         verbose_name_plural = "Товары"
#         indexes = [
#             models.Index(fields=['sku']),
#             models.Index(fields=['name']),
#         ]
# # генерация рандомного SKU
#     def save(self, *args, **kwargs):
#         if not self.sku:
#
#             self.sku = uuid.uuid4().hex[:32].upper()
#         super().save(*args, **kwargs)
#
#     def __str__(self):
#         return f"{self.name} ({self.sku})"
#
