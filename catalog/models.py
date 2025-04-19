from django.db import models

from django.db import models
from django.db.models import JSONField
from django.utils.text import slugify
import uuid

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)

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


class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_info = models.TextField(blank=True)

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"

    def __str__(self):
        return self.name

#добавить описание и характеристики
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    characteristics = JSONField(blank=True, default=dict)
    sku = models.CharField(
        max_length=32, unique=True, editable=False,
        help_text="Уникальный артикул (UUID без дефисов)"
    )
    price = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products'
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name='products'
    )
    stock = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['name']),
        ]
# генерация рандомного SKU
    def save(self, *args, **kwargs):
        if not self.sku:

            self.sku = uuid.uuid4().hex[:32].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.sku})"

