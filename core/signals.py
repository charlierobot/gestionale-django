# core/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Ordine


@receiver(pre_save, sender=Ordine)
def salva_stato_precedente(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Ordine.objects.get(pk=instance.pk)
            instance._stato_precedente = old.stato
        except Ordine.DoesNotExist:
            instance._stato_precedente = None
    else:
        instance._stato_precedente = None


@receiver(post_save, sender=Ordine)
def notifica_cambio_stato(sender, instance, created, **kwargs):
    if created:
        return  # Non notificare alla creazione

    stato_precedente = getattr(instance, '_stato_precedente', None)
    if stato_precedente and stato_precedente != instance.stato:
        send_mail(
            subject=f'Ordine #{instance.id} - Aggiornamento stato',
            message=f'''Ciao {instance.cliente.username},

Il tuo ordine #{instance.id} è stato aggiornato.
Nuovo stato: {instance.get_stato_display()}
Grazie per aver scelto il nostro servizio!''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.cliente.email],
            fail_silently=True,
        )
