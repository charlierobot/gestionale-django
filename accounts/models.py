from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):

    class Ruolo(models.TextChoices):
        CLIENTE = 'CLI', 'Cliente'
        FORNITORE = 'FOR', 'Fornitore'
        ADMIN = 'ADM', 'Amministratore'

    ruolo = models.CharField(
        max_length=3,
        choices=Ruolo.choices,
        default=Ruolo.CLIENTE,
    )

    telefono = models.CharField(max_length=20, blank=True)
    indirizzo = models.TextField(blank=True)