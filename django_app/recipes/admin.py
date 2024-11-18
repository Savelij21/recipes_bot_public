from django.contrib import admin

from .models import Recipe, RecipeIngredient, Ingredient, Category, RecipeCategory, CaloriesRange


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeCategoryInline(admin.TabularInline):
    model = RecipeCategory
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')
    list_display_links = ('id', 'title',)
    readonly_fields = ('id', 'created_at')
    inlines = (RecipeIngredientInline, RecipeCategoryInline)
    search_fields = ('title',)
    search_help_text = 'Искать по названию рецепта'

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'cook_process'),
        }),
        ('К/Б/Ж/У', {
            'fields': ('calories', 'protein', 'fat', 'carbs')
        }),
        ('Сервисная информация', {
            'fields': ('chanel_url', 'video_tg_file_id', 'created_at')
        })
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'unit', 'use_for_catalog')
    list_display_links = ('id', 'name',)
    list_editable = ('unit', 'use_for_catalog')
    ordering = ('name',)
    readonly_fields = ('id',)
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'beauty_title')
    list_display_links = ('id', 'title',)
    ordering = ('title',)
    readonly_fields = ('id',)
    search_fields = ('title', 'beauty_title')


@admin.register(CaloriesRange)
class CaloriesRangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'min', 'max')
    list_display_links = ('id',)
    list_editable = ('min', 'max')
    readonly_fields = ('id',)
    search_fields = ('min', 'max')
