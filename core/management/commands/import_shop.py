import yaml
from django.core.management.base import BaseCommand
from django.db import transaction
from catalog.models import (
    Shop, Category, Product, ProductInfo,
    Parameter, ProductParameter
)

class Command(BaseCommand):
    help = 'Импортирует каталог из YAML-файла'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f', '--file',
            required=True,
            help='Путь до YAML-файла, например data/shop1.yaml'
        )

    def handle(self, *args, **options):
        path = options['file']
        with open(path, encoding='utf-8') as stream:
            data = yaml.safe_load(stream)

        with transaction.atomic():
            # 1. Магазин
            shop_obj, _ = Shop.objects.get_or_create(
                name=data['shop']
            )

            # 2. Категории
            for cat in data['categories']:
                cat_obj, _ = Category.objects.get_or_create(
                    external_id=cat['id'],
                    defaults={'name': cat['name']}
                )
                cat_obj.shops.add(shop_obj)

            # 3. Товары и ProductInfo
            for item in data['goods']:
                # категория по внешнему ID
                cat_obj = Category.objects.get(external_id=item['category'])
                # сам продукт
                prod_obj, _ = Product.objects.get_or_create(
                    external_id=item['id'],
                    defaults={'name': item['name'], 'category': cat_obj}
                )
                # информация о товаре в конкретном магазине
                pi_obj, _ = ProductInfo.objects.update_or_create(
                    product=prod_obj,
                    shop=shop_obj,
                    defaults={
                        'name':      item['name'],
                        'quantity':  item['quantity'],
                        'price':     item['price'],
                        'price_rrc': item['price_rrc'],
                    }
                )

                # 4. Параметры товара
                for pname, pvalue in item.get('parameters', {}).items():
                    param_obj, _ = Parameter.objects.get_or_create(name=pname)
                    ProductParameter.objects.update_or_create(
                        product_info=pi_obj,
                        parameter=param_obj,
                        defaults={'value': str(pvalue)}
                    )

            self.stdout.write(
                self.style.SUCCESS(f'Импорт магазина "{shop_obj.name}" завершён')
            )
