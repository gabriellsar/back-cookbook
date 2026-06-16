from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from infra.models import Recipe, Ingredient, Step
from .serializers import RecipeSerializer, IngredientSerializer, StepSerializer

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-created_at')
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def fork(self, request, pk=None):
        original_recipe = self.get_object()
        user = request.user

        new_recipe = Recipe.objects.create(
            author=user,
            title=f"{original_recipe.title} (Versão de {user.username})",
            description=original_recipe.description,
            forked_from=original_recipe,
            affectionate_note=request.data.get('affectionate_note', '')
        )

        for item in original_recipe.ingredients.all():
            Ingredient.objects.create(
                recipe=new_recipe,
                name=item.name,
                quantity=item.quantity,
                is_locked=item.is_locked # Herda o status de bloqueio do Guardião
            )

        for step in original_recipe.steps.all():
            Step.objects.create(
                recipe=new_recipe,
                order=step.order,
                instruction=step.instruction,
                is_locked=step.is_locked # Herda o status de bloqueio
            )
        serializer = self.get_serializer(new_recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticated]

    def _is_item_protected(self, instance, user):
        if instance.is_locked:
            if instance.recipe.forked_from is not None or instance.recipe.author != user:
                return True
        return False

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if self._is_item_protected(instance, request.user):
            return Response(
                {"detail": "Este ingrediente é um segredo de família trancado pelo Guardião original e não pode ser alterado."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if self._is_item_protected(instance, request.user):
            return Response(
                {"detail": "Este ingrediente é um segredo de família trancado e não pode ser excluído."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

class StepViewSet(viewsets.ModelViewSet):
    queryset = Step.objects.all()
    serializer_class = StepSerializer
    permission_classes = [IsAuthenticated]
    
    def _is_item_protected(self, instance, user):
        if instance.is_locked:
            if instance.recipe.forked_from is not None or instance.recipe.author != user:
                return True
        return False

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if self._is_item_protected(instance, request.user):
            return Response(
                {"detail": "Este passo é um segredo de família trancado e não pode ser alterado."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
        
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if self._is_item_protected(instance, request.user):
            return Response(
                {"detail": "Este passo é um segredo de família trancado e não pode ser excluído."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)