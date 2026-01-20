from django.db import models
from django.conf import settings
from accounts.models import CustomUser

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    attiva = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorie"

    def __str__(self):
        return self.nome


class Fornitore(models.Model):
    ragione_sociale = models.CharField(max_length=150)
    partita_iva = models.CharField(max_length=11, unique=True)
    indirizzo = models.CharField(max_length=255)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    utente = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'ruolo': 'FORNITORE'},
        related_name='categorie_fornite'
    )

    class Meta:
        verbose_name = "Fornitore"
        verbose_name_plural = "Fornitori"
    prodotti = models.ManyToManyField(
        'Prodotto',
        related_name='fornitori',
        blank=True
    )
    def __str__(self):
        return self.ragione_sociale

def default_categoria():
    return Categoria.objects.get_or_create(nome='Generico', attiva=True)

def default_fornitore():
    return Fornitore.objects.get_or_create(ragione_sociale='Generico')

class Prodotto(models.Model):
    nome = models.CharField(max_length=100)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET(default_categoria),
        null=True,
        blank=True,
        related_name='prodotti'
    )
    descrizione = models.TextField(blank=True)
    prezzo = models.DecimalField(max_digits=8, decimal_places=2)
    codice = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )
    quantita = models.IntegerField(default=0)
    fornitore = models.ForeignKey(
        Fornitore,
        on_delete=models.SET(default_fornitore),
        null=True,
        blank=True,
        related_name='prodotti_forniti'
    )
    attivo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Prodotto"
        verbose_name_plural = "Prodotti"
    def __str__(self):
        return self.nome


class Ordine(models.Model):
    class Stato(models.TextChoices):
        PENDING = 'PEN', 'In attesa'
        CONFERMATO = 'CON', 'Confermato'
        SPEDITO = 'SPE', 'Spedito'
        CONSEGNATO = 'DEL', 'Consegnato'
        ANNULLATO = 'ANN', 'Annullato'

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ordini'
    )
    data_ordine = models.DateTimeField(auto_now_add=True)
    stato = models.CharField(
        max_length=3,
        choices=Stato.choices,
        default=Stato.PENDING
    )
    totale = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ['-data_ordine']


class OrdineDettaglio(models.Model):
    ordine = models.ForeignKey(
        Ordine,
        on_delete=models.CASCADE,
        related_name='dettagli'
    )
    prodotto = models.ForeignKey(Prodotto, on_delete=models.PROTECT)
    quantita = models.PositiveIntegerField()
    prezzo_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotale(self):
        return self.quantita * self.prezzo_unitario