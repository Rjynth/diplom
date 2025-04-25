# Dockerfile

# 1. Базовый образ с Python
FROM python:3.10-slim

# 2. Рабочая директория в контейнере
WORKDIR /app

# 3. Копируем файл зависимостей и устанавливаем пакеты
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Копируем весь код проекта
COPY . .

# 5. Открываем порт
EXPOSE 8000

# 6. По умолчанию запускаем dev-сервер
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
