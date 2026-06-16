from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        GUARDIAN = 'GUARDIAN', _('Guardião')
        HEIR = 'HEIR', _('Herdeiro')

    role = models.CharField(
        max_length=15, 
        choices=Role.choices, 
        default=Role.HEIR,
        help_text="Define o nível de permissão (Guardião bloqueia ingredientes, Herdeiro deriva)."
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='recipes'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    forked_from = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='derivations',
        help_text="Se vazio, é uma Receita Raiz. Se preenchido, aponta para a receita original."
    )

    affectionate_note = models.TextField(
        blank=True, 
        null=True,
        help_text="Ex: 'Fiz essa versão lembrando dos domingos na fazenda'."
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.forked_from:
            return f"{self.title} (Fork de {self.forked_from.title})"
        return self.title

class LockableRecipeComponent(models.Model):
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


class Ingredient(LockableRecipeComponent):
    name = models.CharField(max_length=150)
    quantity = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.quantity} de {self.name} {self.lock_status_text}"


class Step(LockableRecipeComponent):
    order = models.PositiveIntegerField(
        help_text="A ordem de execução (1, 2, 3...)"
    )
    instruction = models.TextField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Passo {self.order} {self.lock_status_text}"