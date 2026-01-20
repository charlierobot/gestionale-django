from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class RegistrazioneForm(UserCreationForm):
    RUOLI_REGISTRAZIONE = [
        ('CLI', 'Cliente'),
        ('FOR', 'Fornitore'),
    ]

    ruolo = forms.ChoiceField(choices=RUOLI_REGISTRAZIONE)

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'ruolo',
            'password1',
            'password2', 
        )  

