from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
import datetime
import os
from boto3 import Session
from dotenv import load_dotenv


@csrf_exempt
@require_POST
def create_backup(request):
    # ------------ СОЗДАНИЕ ФАЙЛА БЭКАПА --------------------
    # Создаем папку для бэкапов, если её нет
    backups_dir = os.path.join(settings.BASE_DIR, 'backups')
    if not os.path.exists(backups_dir):
        os.makedirs(backups_dir)

    # Создаем имя файла для бэкапа, например, базы данных SQLite
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_name = f'zhzhgis_recipes__db_backup__{timestamp}.sqlite3'
    backup_path = os.path.join(backups_dir, backup_name)

    # Команда для создания бэкапа SQLite базы данных
    os.system(f'sqlite3 {settings.DATABASES["default"]["NAME"]} ".backup {backup_path}"')

    # ----------------- СОХРАНЕНИЕ БЭКАПА НА YANDEX CLOUD ----------------------------
    load_dotenv()

    endpoint = "https://storage.yandexcloud.net"
    bucket_name = 'zhzhgis-recipes-bot-bucket'

    session = Session()
    s3 = session.client(
            service_name='s3',
            endpoint_url=endpoint,
            region_name="ru-central1",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )

    s3.upload_file(
        backup_path,
        bucket_name,
        f'backups_{os.getenv("ENV")}/{backup_name}'
    )

    return JsonResponse({'message': f'Бэкап БД "{backup_path}" успешно создан и сохранен на Yandex Cloud'})


