# Diplom Backend — Автоматизация закупок в розничной сети

## Описание

Сервис предоставляет API для заказа товаров из нескольких магазинов.  
Основные возможности:
- Регистрация и JWT-аутентификация (SimpleJWT)
- Каталог товаров с поставщиками, параметрами, ценами и наличием
- Работа с корзиной: добавление, удаление, просмотр
- CRUD контактов пользователя (телефон и адреса)
- Подтверждение заказа (перенос из корзины в заказ) с отправкой e-mail
- Просмотр списка заказов, деталей заказа, изменение статуса (для staff)
- Полная реализация сценария «end-to-end»


## Установка

1. Клонировать репозиторий:
   ```bash
   git clone https://github.com/Rjynth/diplom.git
   cd python-final-diplom
   ```
## Создать и активировать виртуальное окружение:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
## Установить зависимости:
```bash
pip install -r requirements.txt
```
## Запустить дев-сервер:
```bash
python manage.py runserver
```

## Конфигурация e-mail
### Для разработки письма выводятся в консоль:
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```


# Тестирование
### 1.  Запуск unit-тестов Django:

```bash
python manage.py test
```
### 2. Postman: импортируйте коллекцию
postman_collection.json

и установите в окружении переменную base_url = http://127.0.0.1:8000.
 #                                                                               
#                                                                               
#                                                                               
#                                                                               
#                                                                               
#                                                                               
#                                                                               
#                                                                               
#                                                                               
#                                                                               
#                                                                               

Тестовый зарегестрированный юзер:

    "user": {
        "id": 3,
        "first_name": "test",
        "last_name": "test1",
        "email": "test@example.com"
    },
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc0NTY3OTkyNCwiaWF0IjoxNzQ1NTkzNTI0LCJqdGkiOiI3YWYwMDJmYjA1OTA0NmYxOWE3NGNhMGY1NDMxYjMzMyIsInVzZXJfaWQiOjN9.p1CQ_fhT7fcsDzqcFyTEft3hBCFeZz7IcUjQryVWbvw",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ1NTkzODI0LCJpYXQiOjE3NDU1OTM1MjQsImp0aSI6ImE2NDBiYTQ4YmFkYzQ5ODM5NzRkNjE1OTliYjJhNjAxIiwidXNlcl9pZCI6M30.wvN5LebQok6h0bYID6qfPCjS8e5z3dXgUM-QgOOTe8Q"



#                                                                               
#                                                                               

  "first_name": "test",

  "last_name":  "test1",

  "email":      "test@example.com",

  "password":   "12345678"


#                                                                               
#                                                                               




superuser:

1           //name



1@mail.com    //mail


1             //password

