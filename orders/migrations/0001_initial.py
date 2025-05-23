# Generated by Django 5.2 on 2025-04-20 15:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('catalog', '0003_parameter_productinfo_productparameter_shop_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('PHONE', 'Телефон'), ('ADDRESS', 'Адрес')], max_length=7, verbose_name='Тип контакта')),
                ('value', models.CharField(blank=True, max_length=50, verbose_name='Значение контакта')),
                ('address', models.JSONField(blank=True, null=True, verbose_name='Данные адреса')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Контакт',
                'verbose_name_plural': 'Контакты',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('NEW', 'Новый'), ('CONFIRMED', 'Подтверждён'), ('ASSEMBLING', 'Сборка'), ('SHIPPED', 'Отгружен'), ('CANCELED', 'Отменён')], default='NEW', max_length=12, verbose_name='Статус заказа')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.order')),
                ('product_info', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='catalog.productinfo')),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='catalog.shop')),
            ],
        ),
    ]
