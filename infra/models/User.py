from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """
    Modelo de Usuário Customizado.
    Permite diferenciar entre dois tipos de usuários: Guardião e Herdeiro.
    """

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