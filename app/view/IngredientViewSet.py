from .RecipeViewSet import *

@extend_schema_view(
    list=extend_schema(
        summary="Listar ingredientes",
        description="Retorna uma lista de todos os ingredientes disponíveis no sistema.",
        tags=['Ingredientes']
    ),
    retrieve=extend_schema(
        summary="Detalhar ingrediente",
        description="Retorna os detalhes de um ingrediente específico.",
        tags=['Ingredientes']
    ),
    create=extend_schema(
        summary="Criar ingrediente",
        description="Adiciona um novo ingrediente à base de dados.",
        tags=['Ingredientes']
    ),
    update=extend_schema(
        summary="Atualizar ingrediente",
        description="Atualiza todos os dados de um ingrediente existente. Falha caso o ingrediente seja um 'segredo de família' trancado por outro usuário.",
        tags=['Ingredientes'],
        responses={
            200: IngredientSerializer,
            403: OpenApiResponse(description="Este ingrediente é um segredo de família trancado e não pode ser alterado.")
        }
    ),
    partial_update=extend_schema(
        summary="Atualização parcial do ingrediente",
        description="Atualiza campos específicos de um ingrediente.",
        tags=['Ingredientes']
    ),
    destroy=extend_schema(
        summary="Deletar ingrediente",
        description="Remove um ingrediente do sistema. Falha caso o ingrediente seja um 'segredo de família' trancado por outro usuário.",
        tags=['Ingredientes'],
        responses={
            204: OpenApiResponse(description="Ingrediente excluído com sucesso."),
            403: OpenApiResponse(description="Este ingrediente é um segredo de família trancado e não pode ser excluído.")
        }
    )
)
class IngredientViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar o CRUD de Ingredientes.
    Permite listar, criar, detalhar, atualizar e deletar ingredientes.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticated]

    def _is_item_protected(self, instance, user):
        # Protege ingredientes que são "segredos de família" em receitas forked
        if instance.is_locked:
            if instance.recipe.forked_from is not None or instance.recipe.author != user:
                return True
        return False

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if self._is_item_protected(instance, request.user):
            return Response(
                {"detail": "Este ingrediente é um segredo de família trancado e não pode ser alterado."},
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