from celery import shared_task
from django.core.mail import send_mail

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