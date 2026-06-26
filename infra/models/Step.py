from django.db import models
from ._LockableRecipeComponent import _LockableRecipeComponent

class Step(_LockableRecipeComponent):
    """
    Representa um passo de preparo de uma Receita.
    Ordenado automaticamente pelo campo 'step_number'. 
    Também suporta a proteção de 'segredo de família'.
    """
    step_number = models.PositiveIntegerField(
        help_text="A ordem de execução (1, 2, 3...)"
    )
    instruction = models.TextField()

    class Meta:
        app_label = 'infra'
        ordering = ['step_number']
        verbose_name = 'Passo'
        verbose_name_plural = 'Passos'

    def __str__(self):
        return f"Passo {self.step_number}"
