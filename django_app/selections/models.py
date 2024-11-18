from django.db import models


class ProductsSelection(models.Model):
    """Подборки продуктов"""

    title = models.CharField(max_length=100, unique=True, verbose_name='Название подборки')
    beauty_title = models.CharField(max_length=30, unique=True, verbose_name='Название подборки в боте')
    description = models.TextField(verbose_name='Описание подборки')

    video_url = models.URLField(verbose_name='Ссылка на видео')

    created_at = models.DateTimeField(auto_now_add=True)

    num = models.PositiveIntegerField(default=0, verbose_name='Порядковый номер в боте')

    class Meta:
        verbose_name = 'Подборка'
        verbose_name_plural = 'Подборки'

    def __str__(self):
        return f'#{self.pk} {self.title}'
