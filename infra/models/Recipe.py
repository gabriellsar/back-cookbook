from django.db import models
from django.conf import settings

class Recipe(models.Model):
    """
    Entidade principal que representa uma Receita no sistema.
    Armazena dados básicos e gerencia o relacionamento de 'Fork' 
    (clonagem de receitas entre usuários).
    """
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, 
        related_name='recipes'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    prep_time = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Tempo de preparo em minutos."
    )
    servings = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Rendimento da receita (número de porções)."
    )
    video_url = models.URLField(
        blank=True,
        null=True,
        help_text="Link opcional para um vídeo do preparo."
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Lista de tags/categorias da receita (ex.: vegano, rápido)."
    )

    forked_from = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='forks'
    )
    affectionate_note = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'infra'
        verbose_name = 'Receita'
        verbose_name_plural = 'Receitas'

    def __str__(self):
        if self.forked_from:
            return f"{self.title} (Fork de {self.forked_from.title})"
        return self.title