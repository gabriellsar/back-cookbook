from django.db import models
from infra.models import _LockableRecipeComponent

class Ingredient(_LockableRecipeComponent):
    """
    Representa um ingrediente específico de uma Receita.
    Herda de _LockableRecipeComponent para permitir bloqueio de edição em forks.
    """
    name = models.CharField(max_length=100)
    quantity = models.CharField(max_length=100)

    class Meta:
        app_label = 'infra'
        verbose_name = 'Ingrediente'
        verbose_name_plural = 'Ingredientes'

    def __str__(self):
        return f"{self.quantity} de {self.name}"
