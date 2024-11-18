from django.contrib import admin
from .models import TgUsers


@admin.register(TgUsers)
class TgUsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'tg_id', 'username', 'name', 'subscribed')
    list_display_links = ('id', 'tg_id',)
    readonly_fields = ('id', 'created_at')
    search_fields = ('tg_id', 'name',)
    ordering = ('-created_at',)
