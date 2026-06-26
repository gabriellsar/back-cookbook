from django.db import models
    
class _LockableRecipeComponent(models.Model):
    """
    Componente abstrato para representar elementos de uma Receita/Step que podem ser bloqueados.
    """

    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE, 
        related_name='%(class)ss' 
    )
    is_locked = models.BooleanField(
        default=False,
        help_text="Se True, usuários que fizerem fork desta receita não poderão alterar ou remover este item."
    )

    class Meta:
        abstract = True

    @property
    def lock_status_text(self):
        return "lock" if self.is_locked else "unlock"
