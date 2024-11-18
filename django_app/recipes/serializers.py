from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Recipe, Ingredient, Category, CaloriesRange


class RecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    recipes_count = SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = '__all__'

    def get_recipes_count(self, obj: Category) -> int:
        return obj.recipe_set.count()


class CategorySerializer(ModelSerializer):
    recipes_count = SerializerMethodField()

    class Meta:
        model = Category
        fields = '__all__'

    def get_recipes_count(self, obj: Category) -> int:
        return obj.recipe_set.count()


class CaloriesRangeSerializer(ModelSerializer):
    recipes_count = SerializerMethodField()

    class Meta:
        model = CaloriesRange
        fields = '__all__'

    def get_recipes_count(self, obj: CaloriesRange) -> int:
        return Recipe.objects.filter(calories__gte=obj.min, calories__lte=obj.max).count()
