from celery import shared_task
from django.core.mail import send_mail
from easy_thumbnails.files import get_thumbnailer
from django.apps import apps
from django.conf import settings

@shared_task
def send_registration_email(email, full_name):
    subject = f'Добро пожаловать, {full_name}!'
    message = (
        'Спасибо за регистрацию на нашем сервисе. '
        'Теперь вы можете добавлять товары в корзину и подтверждать заказы.'
    )
    send_mail(subject, message, 'no-reply@yourshop.com', [email])

@shared_task
def send_order_confirmation_email(order_id, email, full_name, total_sum, status):
    subject = f'Ваш заказ #{order_id} подтверждён'
    message = (
        f'Здравствуйте, {full_name}!\n\n'
        f'Ваш заказ #{order_id} успешно создан.\n'
        f'Сумма заказа: {total_sum:.2f}.\n'
        f'Статус: {status}.\n\n'
        'Спасибо за покупку!'
    )
    send_mail(subject, message, 'no-reply@yourshop.com', [email])




@shared_task
def generate_thumbnails(model_label: str, pk: int, field_name: str):
    """
    model_label — 'app_label.ModelName'
    pk          — первичный ключ экземпляра
    field_name  — имя поля ImageField
    """
    Model = apps.get_model(model_label)
    instance = Model.objects.filter(pk=pk).first()
    if not instance:
        return

    img = getattr(instance, field_name)
    if not img:
        return

    # прогоняем всё, что прописано в THUMBNAIL_ALIASES['']
    for alias in settings.THUMBNAIL_ALIASES.get('', {}):
        get_thumbnailer(img).get_thumbnail(alias)