from django.db import models


class TgUsers(models.Model):
    tg_id = models.IntegerField(unique=True)
    username = models.CharField(max_length=256, null=True)
    name = models.CharField(max_length=256)
    first_name = models.CharField(max_length=256, null=True)
    last_name = models.CharField(max_length=256, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    subscribed = models.BooleanField(default=True)
    blocked = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'TG Пользователь'
        verbose_name_plural = 'TG Пользователи'

    def __str__(self):
        return f'{self.tg_id}#{self.username}'

