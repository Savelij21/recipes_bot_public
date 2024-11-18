from django.contrib import admin
from .models import ProductsSelection


@admin.register(ProductsSelection)
class ProductsSelectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'beauty_title', 'num')
    list_display_links = ('id', 'beauty_title',)
    readonly_fields = ('id', 'created_at')
    search_fields = ('title', 'beauty_title',)
    list_editable = ('num',)
    ordering = ('num',)
