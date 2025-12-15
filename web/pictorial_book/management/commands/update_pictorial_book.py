import boto3
from django.conf import settings
from django.core.management.base import BaseCommand
from pictorial_book.models import HairStyleDictionary, HairStyleImage

class Command(BaseCommand):
    help = "Load pictorial book images from S3 into DB"

    def handle(self, *args, **kwargs):
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )

        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        prefix = 'pictorial_book/'

        self.stdout.write(self.style.WARNING(f"S3 버킷에서 파일 목록 가져오는 중: {bucket_name}/{prefix}"))

        try:
            paginator = s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

            for page in pages:
                if 'Contents' not in page:
                    self.stdout.write(self.style.WARNING(f"'{prefix}' 경로에 파일이 없습니다."))
                    continue

                for obj in page['Contents']:
                    # 파일 경로 파싱: pictorial_book/{gender}/{category}/{name}/{length}/{filename}
                    file_path = obj['Key']

                    # 디렉토리는 건너뛰기
                    if file_path.endswith('/'):
                        continue

                    parts = file_path.split('/')

                    if len(parts) != 6:  # pictorial_book, gender, category, name, length, filename
                        self.stdout.write(self.style.WARNING(f"잘못된 경로 구조: {file_path}"))
                        continue

                    _, gender, category, name, length, filename = parts

                    # HairStyleDictionary 생성 또는 가져오기
                    dict_obj, created = HairStyleDictionary.objects.get_or_create(
                        name=name,
                        gender=gender,
                        category=category,
                        defaults={"description": ""}
                    )

                    # HairStyleImage 생성 (중복 체크)
                    if not HairStyleImage.objects.filter(
                        name_gender=dict_obj,
                        length=length,
                        image_path=file_path
                    ).exists():
                        HairStyleImage.objects.create(
                            name_gender=dict_obj,
                            length=length,
                            image_path=file_path
                        )
                        self.stdout.write(self.style.SUCCESS(f"✓ 추가: {file_path}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"- 이미 존재: {file_path}"))

            self.stdout.write(self.style.SUCCESS("\n완료!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"에러 발생: {str(e)}"))
