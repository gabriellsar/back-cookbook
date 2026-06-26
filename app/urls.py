from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .view.IngredientViewSet import IngredientViewSet
from .view.RecipeViewSet import RecipeViewSet
from .view.StepViewSet import StepViewSet

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'steps', StepViewSet, basename='step')

urlpatterns = [
    path('', include(router.urls)),
]