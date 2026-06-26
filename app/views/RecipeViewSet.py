from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view, extend_schema_view
    
from app.serializers import RecipeSerializer, IngredientSerializer, StepSerializer
from infra.models import *

@extend_schema_view(
    list=extend_schema(
        summary="Listar todas as receitas",
        description="Retorna uma lista de todas as receitas cadastradas, ordenadas das mais recentes para as mais antigas.",
        tags=['Receitas']
    ),
    retrieve=extend_schema(
        summary="Detalhar uma receita",
        description="Retorna todos os detalhes de uma receita específica através do seu ID.",
        tags=['Receitas']
    ),
    create=extend_schema(
        summary="Criar uma nova receita",
        description="Cadastra uma nova receita no sistema e a associa automaticamente ao usuário autenticado.",
        tags=['Receitas']
    ),
    update=extend_schema(
        summary="Atualizar receita completa",
        description="Atualiza integralmente os dados de uma receita existente.",
        tags=['Receitas']
    ),
    partial_update=extend_schema(
        summary="Atualização parcial de receita",
        description="Atualiza campos específicos de uma receita.",
        tags=['Receitas']
    ),
    destroy=extend_schema(
        summary="Deletar receita",
        description="Remove uma receita do banco de dados.",
        tags=['Receitas']
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar o CRUD de Receitas.
    Permite listar, criar, detalhar, atualizar e deletar receitas.
    Inclui a funcionalidade avançada de 'Fork' para clonar receitas.
    """

    queryset = Recipe.objects.all().order_by('-created_at')
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @extend_schema(
        summary="Clonar (Fork) uma receita",
        description="Cria uma cópia exata de uma receita existente (incluindo ingredientes e passos com status de segredo) associando a nova versão ao usuário que fez a requisição.",
        responses={
            200: OpenApiResponse(description="Receita clonada com sucesso."),
            401: OpenApiResponse(description="O usuário precisa estar autenticado para dar fork."),
            404: OpenApiResponse(description="Receita original não encontrada.")
        },
        tags=['Receitas - Ações Customizadas']
    )
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
            new_recipe.ingredients.create(
                name=item.name,
                quantity=item.quantity,
                is_locked=item.is_locked
            )

        for step in original_recipe.steps.all():
            new_recipe.steps.create(
                step_number=step.step_number,
                instruction=step.instruction,
                is_locked=step.is_locked
            )

        serializer = self.get_serializer(new_recipe)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Avaliar uma receita",
        description="Registra ou atualiza a nota (1 a 5) do usuário autenticado para a receita. Retorna a receita atualizada com a média recalculada.",
        responses={
            200: OpenApiResponse(description="Avaliação registrada."),
            400: OpenApiResponse(description="Nota inválida (deve ser um inteiro de 1 a 5)."),
            401: OpenApiResponse(description="O usuário precisa estar autenticado para avaliar.")
        },
        tags=['Receitas - Ações Customizadas']
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def rate(self, request, pk=None):
        recipe = self.get_object()

        try:
            value = int(request.data.get('value'))
        except (TypeError, ValueError):
            return Response(
                {'detail': 'O campo "value" deve ser um inteiro de 1 a 5.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if value < 1 or value > 5:
            return Response(
                {'detail': 'A nota deve estar entre 1 e 5.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Rating.objects.update_or_create(
            recipe=recipe,
            user=request.user,
            defaults={'value': value}
        )

        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_200_OK)
