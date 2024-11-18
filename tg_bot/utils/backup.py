
import aioboto3
from dotenv import load_dotenv
import os


async def send_backup_to_yandex_cloud(path_to_backups_dir: str, backup_name: str):
    load_dotenv()

    endpoint = "https://storage.yandexcloud.net"
    bucket_name = os.getenv('AWS_BUCKET_NAME')

    session = aioboto3.Session()

    async with session.client(
        service_name='s3',
        endpoint_url=endpoint,
        region_name="ru-central1",
        aws_access_key_id=os.getenv('ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('SECRET_ACCESS_KEY')
    ) as s3:

        await s3.upload_file(
            path_to_backups_dir,
            bucket_name,
            f'backups_{os.getenv("ENV")}/{backup_name}'
        )



