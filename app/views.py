from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from infra.models import Recipe, Ingredient, Step
from .serializers import RecipeSerializer, IngredientSerializer, StepSerializer

class RecipeViewSet(viewsets.ModelViewSet):
    """
    CRUD completo para Receitas.
    Atende ao requisito: "Pelo menos um endpoint protegido" (IsAuthenticatedOrReadOnly)
    """
    queryset = Recipe.objects.all().order_by('-created_at')
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Quando criar uma receita do zero, o autor é o usuário logado
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def fork(self, request, pk=None):
        """
        A GRANDE INOVAÇÃO: A lógica do "Git Fork".
        Copia uma receita raiz, incluindo ingredientes e passos.
        """
        original_recipe = self.get_object()
        user = request.user

        # 1. Cria a nova receita derivada
        new_recipe = Recipe.objects.create(
            author=user,
            title=f"{original_recipe.title} (Versão de {user.username})",
            description=original_recipe.description,
            forked_from=original_recipe,
            affectionate_note=request.data.get('affectionate_note', '')
        )

        # 2. Copia os ingredientes
        for item in original_recipe.ingredients.all():
            Ingredient.objects.create(
                recipe=new_recipe,
                name=item.name,
                quantity=item.quantity,
                is_locked=item.is_locked # Herda o status de bloqueio do Guardião
            )

        # 3. Copia os passos
        for step in original_recipe.steps.all():
            Step.objects.create(
                recipe=new_recipe,
                order=step.order,
                instruction=step.instruction,
                is_locked=step.is_locked # Herda o status de bloqueio
            )

        # Retorna a nova receita criada
        serializer = self.get_serializer(new_recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_locked and instance.recipe.author != request.user:
            return Response(
                {"detail": "Este ingrediente é um segredo de família trancado pelo Guardião original e não pode ser alterado."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

class StepViewSet(viewsets.ModelViewSet):
    queryset = Step.objects.all()
    serializer_class = StepSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_locked and instance.recipe.author != request.user:
            return Response(
                {"detail": "Este passo é um segredo de família trancado e não pode ser alterado."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)