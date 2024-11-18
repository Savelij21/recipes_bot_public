from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название ингредиенты')
    unit = models.CharField(max_length=10, verbose_name='Единица измерения')  # например, 'гр', 'мл', 'шт'
    use_for_catalog = models.BooleanField(default=True, verbose_name='Использовать в каталоге')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'#{self.pk} {self.name} ({self.unit})'


class Category(models.Model):
    title = models.CharField(max_length=100, unique=True, verbose_name='Название категории')
    beauty_title = models.CharField(max_length=30, unique=True, verbose_name='Название категории в боте')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return f'#{self.pk} {self.title}'


class Recipe(models.Model):
    title = models.CharField(max_length=30, unique=True, verbose_name='Название')
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient', verbose_name='Ингредиенты')
    cook_process = models.TextField(verbose_name='Описание приготовления')

    calories = models.IntegerField(verbose_name='Калории')  # per 100 grams
    protein = models.IntegerField(verbose_name='Белки')  # per 100 grams
    fat = models.IntegerField(verbose_name='Жиры')  # per 100 grams
    carbs = models.IntegerField(verbose_name='Углеводы')  # per 100 grams
    # serving_weight = models.IntegerField(verbose_name='Вес одной порции', blank=True, null=True)  # grams

    categories = models.ManyToManyField(Category, through='RecipeCategory', verbose_name='Категории')

    chanel_url = models.URLField(verbose_name='Ссылка на рецепт в канале')
    video_tg_file_id = models.CharField(max_length=200, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.title


# for ManyToMany
class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT, verbose_name='Рецепт')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT, verbose_name='Ингредиент')
    quantity = models.IntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return f"{self.quantity} {self.ingredient.unit} of {self.ingredient.name} in {self.recipe.title}"


class RecipeCategory(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT, verbose_name='Рецепт')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Категория')

    class Meta:
        verbose_name = 'Категория рецепта'
        verbose_name_plural = 'Категории рецептов'


class CaloriesRange(models.Model):
    min = models.IntegerField()
    max = models.IntegerField()

    class Meta:
        verbose_name = 'Диапазон калорий'
        verbose_name_plural = 'Диапазоны калорий'

    def __str__(self):
        return f"{self.min} <---> {self.max}"





