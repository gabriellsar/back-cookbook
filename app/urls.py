from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, IngredientViewSet, StepViewSet

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'steps', StepViewSet, basename='step')

urlpatterns = [
    path('', include(router.urls)),
]