from django.db import models
from django.conf import settings
from catalog.models import ProductInfo, Shop
from django.core.exceptions import ValidationError
from django.db.models import JSONField



class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    dt = models.DateTimeField(auto_now_add=True)
    STATUS_NEW = 'NEW'
    STATUS_CONFIRMED = 'CONFIRMED'
    STATUS_ASSEMBLING = 'ASSEMBLING'
    STATUS_SHIPPED = 'SHIPPED'
    STATUS_CANCELED = 'CANCELED'

    STATUS_CHOICES = [
        (STATUS_NEW, 'Новый'),
        (STATUS_CONFIRMED, 'Подтверждён'),
        (STATUS_ASSEMBLING, 'Сборка'),
        (STATUS_SHIPPED, 'Отгружен'),
        (STATUS_CANCELED, 'Отменён'),
    ]
    status = models.CharField(
        max_length=12,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
        verbose_name='Статус заказа',
    )


class OrderItem(models.Model):
    order        = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_info = models.ForeignKey(ProductInfo, on_delete=models.PROTECT)
    shop         = models.ForeignKey(Shop, on_delete=models.PROTECT)
    quantity     = models.PositiveIntegerField()
    price        = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # 1) Проверяем, что магазин соответствует записи product_info
        if self.product_info.shop_id != self.shop_id:
            raise ValidationError("Магазин в OrderItem должен совпадать с shop из product_info.")

        # 2) Если цена ещё не заполнена, копируем из product_info
        if not self.price:
            self.price = self.product_info.price

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.order} — {self.product_info.name} @ {self.shop.name} × {self.quantity}'



class Contact(models.Model):
    PHONE = 'PHONE'
    ADDRESS = 'ADDRESS'
    TYPE_CHOICES = [
        (PHONE, 'Телефон'),
        (ADDRESS, 'Адрес'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='contacts'
    )
    type = models.CharField(
        max_length=7,
        choices=TYPE_CHOICES,
        verbose_name='Тип контакта'
    )
    # Для телефонов: хранится строка с номером
    value = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Значение контакта'
    )
    # Для адресов: структура {city, street, house, building, apartment…}
    address = JSONField(
        blank=True,
        null=True,
        verbose_name='Данные адреса'
    )

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'

    def clean(self):
        # Проверяем ограничения на количество
        qs = Contact.objects.filter(user=self.user).exclude(pk=self.pk)
        if self.type == self.PHONE:
            if qs.filter(type=self.PHONE).exists():
                raise ValidationError('У пользователя уже есть один телефон.')
            if not self.value:
                raise ValidationError('Нужно указать номер телефона.')
        else:  # ADDRESS
            if qs.filter(type=self.ADDRESS).count() >= 5:
                raise ValidationError('Нельзя добавить более 5 адресов.')
            if not self.address:
                raise ValidationError('Нужно указать данные адреса.')
        super().clean()

    def save(self, *args, **kwargs):
        # Гарантируем, что clean() отработает
        self.full_clean()
        # Очищаем неиспользуемое поле
        if self.type == self.PHONE:
            self.address = None
        else:
            self.value = ''
        super().save(*args, **kwargs)

    def __str__(self):
        if self.type == self.PHONE:
            return f'{self.user}: {self.value}'
        addr = ', '.join(f'{k}={v}' for k, v in self.address.items())
        return f'{self.user}: {addr}'