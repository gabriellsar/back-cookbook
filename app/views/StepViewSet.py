from .RecipeViewSet import *

@extend_schema_view(
    list=extend_schema(
        summary="Listar passos de preparo",
        description="Retorna uma lista de todos os passos de preparo.",
        tags=['Passos (Steps)']
    ),
    retrieve=extend_schema(
        summary="Detalhar passo",
        description="Retorna os detalhes de um passo de preparo específico.",
        tags=['Passos (Steps)']
    ),
    create=extend_schema(
        summary="Criar passo de preparo",
        description="Adiciona um novo passo e o associa a uma receita.",
        tags=['Passos (Steps)']
    ),
    update=extend_schema(
        summary="Atualizar passo",
        description="Atualiza os dados e a ordem de um passo existente. Falha caso seja um 'segredo de família' de outra pessoa.",
        tags=['Passos (Steps)'],
        responses={
            200: StepSerializer,
            403: OpenApiResponse(description="Este passo é um segredo de família trancado e não pode ser alterado.")
        }
    ),
    partial_update=extend_schema(
        summary="Atualização parcial do passo",
        description="Atualiza campos específicos de um passo.",
        tags=['Passos (Steps)']
    ),
    destroy=extend_schema(
        summary="Deletar passo",
        description="Remove um passo do sistema. Falha caso seja um 'segredo de família' de outra pessoa.",
        tags=['Passos (Steps)'],
        responses={
            204: OpenApiResponse(description="Passo excluído com sucesso."),
            403: OpenApiResponse(description="Este passo é um segredo de família trancado e não pode ser excluído.")
        }
    )
)
class StepViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar o CRUD de Steps.
    Permite listar, criar, detalhar, atualizar e deletar Steps.
    """
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