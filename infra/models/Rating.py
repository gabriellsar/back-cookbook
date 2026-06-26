from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Rating(models.Model):
    """
    Avaliação (1 a 5 estrelas) de uma Receita feita por um usuário.
    Cada usuário pode avaliar uma receita apenas uma vez (unique_together);
    uma nova submissão atualiza a nota anterior.
    """
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    value = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Nota de 1 a 5."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'infra'
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        unique_together = ('recipe', 'user')

    def __str__(self):
        return f"{self.user.username} → {self.recipe.title}: {self.value}★"
