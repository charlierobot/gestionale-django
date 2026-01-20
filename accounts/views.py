from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib import messages
from .forms import RegistrazioneForm

User = get_user_model()

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self):
        user = self.request.user

        if user.is_superuser or user.ruolo == 'ADM':
            return reverse_lazy('core:dashboard_admin')
        elif user.ruolo == 'FOR' or user.username == 'fornitore1':
            return reverse_lazy('core:dashboard_fornitore')
        elif user.ruolo == 'CLI' or user.username == 'cliente1':
            return reverse_lazy('core:dashboard_cliente')

def logout_view(request):
    logout(request)
    return redirect('accounts:login') 


def registrazione(request):
    if request.method == 'POST':
        form = RegistrazioneForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registrazione completata con successo!')
            return redirect('accounts:login')
    else:
        form = RegistrazioneForm()
    return render(request, 'accounts/registrazione.html', {'form': form})


