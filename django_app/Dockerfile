
# Докер файл для разработки, чтобы запускать Gunicorn


# Базовый образ
FROM python:3.10

# Установка зависимостей системы
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean

# Установка рабочей директории
WORKDIR /app

# Копирование файла зависимостей
COPY requirements.txt /app/

# Установка зависимостей Python
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода приложения
COPY . /app/

# Установка переменной окружения для Django
ENV DJANGO_SETTINGS_MODULE=src.settings
ENV DJANGO_API_SECRET_KEY='django-insecure-cu$t6j7r@or$e*d)zg4a7d!8!+=v$oynm@6d$=m9!a1ft+u(y&'

# Сборка статики
# RUN python manage.py collectstatic --noinput

# Запуск Gunicorn
CMD ["gunicorn", "-c", "gunicorn_config.py", "src.wsgi:application"]
