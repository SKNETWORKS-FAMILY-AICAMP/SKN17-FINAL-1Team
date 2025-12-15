from django.db import models


class HairStyleDictionary(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=24, verbose_name='도감 이름')
    category = models.CharField(max_length=1, verbose_name='도감 카테고리')
    gender = models.CharField(max_length=1, verbose_name='성별')
    description = models.TextField(verbose_name='헤어스타일 설명')

    class Meta:
        db_table = 'pictorial_book'
        unique_together = ('name', 'gender')


class HairStyleImage(models.Model):
    dict_image_id = models.AutoField(primary_key=True, verbose_name='이미지 식별자')
    name_gender = models.ForeignKey(
        HairStyleDictionary,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='도감 스타일'
    )
    length = models.CharField(max_length=10, verbose_name='헤어스타일 길이')
    image_path = models.CharField(max_length=255, verbose_name='도감 이미지 경로')

    class Meta:
        db_table = 'pictorial_book_image'
