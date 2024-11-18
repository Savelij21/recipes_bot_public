import logging
import random

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Recipe, Ingredient, Category, CaloriesRange
from .serializers import RecipeSerializer, IngredientSerializer, CategorySerializer, CaloriesRangeSerializer

logger = logging.getLogger(__name__)


class RecipeModelViewSet(ModelViewSet):
    queryset = Recipe.objects.all().order_by('-created_at')
    serializer_class = RecipeSerializer

    def get_random_recipe(self, request):
        random_recipe = self.queryset.get(pk=random.randint(1, len(self.queryset)))
        serializer = RecipeSerializer(random_recipe, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IngredientModelViewSet(ModelViewSet):
    queryset = Ingredient.objects.all().filter(use_for_catalog=True).order_by('name')
    serializer_class = IngredientSerializer

    def get_ingredient_recipes(self, request, pk):
        ingredient: Ingredient = self.queryset.get(pk=pk)
        recipes = ingredient.recipe_set.all()
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryModelViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_category_recipes(self, request, pk):
        category: Category = self.queryset.get(pk=pk)
        recipes = category.recipe_set.all()
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CaloriesRangeModelViewSet(ModelViewSet):
    queryset = CaloriesRange.objects.all().order_by('min')
    serializer_class = CaloriesRangeSerializer

    def get_calories_range_recipes(self, request, pk):
        calories_range: CaloriesRange = self.queryset.get(pk=pk)
        recipes = Recipe.objects.filter(calories__gte=calories_range.min, calories__lte=calories_range.max)
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
