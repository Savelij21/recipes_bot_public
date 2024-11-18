
from django.urls import path

from .views import RecipeModelViewSet, IngredientModelViewSet, CategoryModelViewSet, CaloriesRangeModelViewSet


urlpatterns = [

    path('recipes/', RecipeModelViewSet.as_view({
            'get': 'list',
    })),
    path('recipes/random/', RecipeModelViewSet.as_view({
            'get': 'get_random_recipe',
    })),


    path('ingredients/', IngredientModelViewSet.as_view({
            'get': 'list',
    })),
    path('ingredients/<int:pk>/', IngredientModelViewSet.as_view({
            'get': 'retrieve',
    })),
    path('ingredients/<int:pk>/recipes/', IngredientModelViewSet.as_view({
            'get': 'get_ingredient_recipes',
    })),


    path('categories/', CategoryModelViewSet.as_view({
            'get': 'list',
    })),
    path('categories/<int:pk>/', CategoryModelViewSet.as_view({
            'get': 'retrieve',
    })),
    path('categories/<int:pk>/recipes/', CategoryModelViewSet.as_view({
            'get': 'get_category_recipes',
    })),


    path('calories_ranges/', CaloriesRangeModelViewSet.as_view({
        'get': 'list',
    })),
    path('calories_ranges/<int:pk>/', CaloriesRangeModelViewSet.as_view({
        'get': 'retrieve',
    })),
    path('calories_ranges/<int:pk>/recipes/', CaloriesRangeModelViewSet.as_view({
        'get': 'get_calories_range_recipes',
    })),
]



