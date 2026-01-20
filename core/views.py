from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum, Count, Q, F
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView
from .cart import Cart
from django.shortcuts import get_object_or_404
from django.contrib import messages

from .models import Prodotto, Categoria, Fornitore, Ordine, OrdineDettaglio

User = get_user_model()


# ==========================
# DASHBOARD FORNITORE
# ==========================
@login_required
def dashboard_fornitore(request):
    if request.user.ruolo != 'FOR' and not request.user.is_superuser:
        return redirect('core:home')

    try:
        fornitore = request.user.fornitore
        prodotti = fornitore.prodotti.all()
        totale_pezzi = prodotti.aggregate(
            totale=Sum('quantita')
        )['totale'] or 0
    except:
        fornitore = None
        prodotti = []
        totale_pezzi = 0

    return render(request, 'core/dashboard_fornitore.html', {
        'fornitore': fornitore,
        'prodotti': prodotti,
        'totale_pezzi': totale_pezzi
    })

# ==========================
# DASHBOARD CLIENTE
# ==========================
@login_required
def dashboard_cliente(request):
    if request.user.ruolo != 'CLI' and not request.user.is_superuser:
        return redirect('core:home')
    
    utente = request.user

    ordini = Ordine.objects.filter(cliente=utente)

    numero_ordini = ordini.count()

    prodotti_acquistati = (
        OrdineDettaglio.objects
        .filter(ordine__in=ordini)
        .aggregate(totale=Sum("quantita"))["totale"] or 0
    )

    totale_speso = (
        OrdineDettaglio.objects
        .filter(ordine__in=ordini)
        .aggregate(
            totale=Sum(F("prezzo_unitario") * F("quantita"))
        )["totale"] or 0
    )

    context = {
        "numero_ordini": numero_ordini,
        "prodotti_acquistati": prodotti_acquistati,
        "totale_speso": totale_speso,
    }

    return render(request, "core/dashboard_cliente.html", context)


# ==========================
# DASHBOARD ADMIN
# ==========================
@login_required
def dashboard_admin(request):
    if not request.user.is_superuser and request.user.ruolo != 'ADM':
        return redirect('home')

    utenti_per_ruolo = ( User.objects.values('ruolo').annotate(count=Count('id')) )

    prodotti_sotto_scorta = Prodotto.objects.filter(quantita__lt=10)
    ultimi_utenti = User.objects.order_by('-date_joined')[:5]

    stats = {
        'totale_utenti': User.objects.all().count(),
        'totale_prodotti': Prodotto.objects.count(),
        'totale_categorie': Categoria.objects.count(),

        'totale_fornitori': Fornitore.objects.count(),
    }

    return render(request, 'core/dashboard_admin.html', {
        'stats': stats,
        'utenti_per_ruolo': utenti_per_ruolo,
        'prodotti_sotto_scorta': prodotti_sotto_scorta,
        'ultimi_utenti': ultimi_utenti,
    })


# REDIRECT HOME (POST-LOGIN)
# ==========================

def home(request):
    return render(request,'core/home.html')
#-------------------------------------------------------

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.ruolo == 'ADM'

class ProdottoListView(ListView):
    model = Prodotto
    template_name = 'core/prodotto_list.html'
    context_object_name = 'prodotti'
    paginate_by = 10

    def get_queryset(self):
        qs = Prodotto.objects.filter(attivo=True)

        categoria = self.request.GET.get('categoria')
        if categoria:
            qs = qs.filter(categoria_id=categoria)

        search = self.request.GET.get('q')
        if search:
            qs = qs.filter(
                Q(nome__icontains=search) |
                Q(codice__icontains=search)
            )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorie'] = Categoria.objects.filter(attiva=True)
        context['categoria_selezionata'] = self.request.GET.get('categoria', '')
        context['search'] = self.request.GET.get('q', '')
        return context


class ProdottoDetailView(DetailView):
    model = Prodotto
    template_name = 'core/prodotto_detail.html'
    context_object_name = 'prodotto'

class ProdottoDeleteView(AdminRequiredMixin, DeleteView):
    model = Prodotto
    template_name = 'core/prodotto_confirm_delete.html'
    success_url = reverse_lazy('prodotto_list')

    def test_func(self):
        return self.request.user.ruolo == 'ADM'

class ProdottoUpdateView(AdminRequiredMixin, UpdateView):
    model = Prodotto
    template_name = 'core/prodotto_form.html'
    fields = ['nome', 'codice', 'descrizione', 'prezzo', 'quantita', 'categoria']
    success_url = reverse_lazy('prodotto_list')

    def test_func(self):
        return self.request.user.ruolo == 'ADM'

class ProdottoCreateView(AdminRequiredMixin, CreateView):
    model = Prodotto
    template_name = 'core/prodotto_form.html'
    fields = ['codice', 'nome', 'descrizione', 'prezzo', 'quantita', 'categoria', 'attivo']
    success_url = reverse_lazy('prodotto_list')

def add_to_cart(request, prodotto_id):
    cart = Cart(request)
    prodotto = get_object_or_404(Prodotto, id=prodotto_id)
    cart.add(prodotto)
    return redirect('cart_detail')

def cart_detail(request):
    cart = Cart(request)

    if request.method == 'POST':
        for item in cart:
            prodotto = item['prodotto']
            qty_key = f'qty_{prodotto.id}'
            if qty_key in request.POST:
                new_qty = int(request.POST[qty_key])
                if new_qty > prodotto.quantita:
                    messages.error(
                        request,
                        f'Solo {prodotto.quantita} disponibili per {prodotto.nome}'
                    )
                elif new_qty > 0:
                    cart.update(prodotto, new_qty)
                else:
                    cart.remove(prodotto)
        messages.success(request, 'Carrello aggiornato!')
        return redirect('cart_detail')


def cart_remove(request, prodotto_id):
    cart = Cart(request)
    prodotto = get_object_or_404(Prodotto, id=prodotto_id)
    cart.remove(prodotto)
    return redirect('cart_detail')

def checkout(request):
    cart = Cart(request)

    if len(cart) == 0:
        return redirect("cart_detail")

    if request.method == 'POST':
        # Verifica disponibilità
        errori = []
        for item in cart:
            prodotto = Prodotto.objects.get(id=item['prodotto'].id)
            if item['qty'] > prodotto.quantita:
                errori.append(
                    f'{prodotto.nome}: disponibili solo {prodotto.quantita}'
                )

        if errori:
            for errore in errori:
                messages.error(request, errore)
            return redirect('cart_detail')

        # Tutto ok, procedi con transazione
        try:
            with transaction.atomic():
                # Crea ordine
                ordine = Ordine.objects.create(
                    cliente=request.user,
                    totale=cart.get_total()
                )

                # Crea dettagli e aggiorna stock
                for item in cart:
                    prodotto = Prodotto.objects.select_for_update().get(
                        id=item['prodotto'].id
                    )

                    OrdineDettaglio.objects.create(
                        ordine=ordine,
                        prodotto=prodotto,
                        quantita=item['qty'],
                        prezzo_unitario=item['price']
                    )

                    # Decrementa quantità
                    prodotto.quantita -= item['qty']
                    prodotto.save()

                cart.clear()
                messages.success(request, f'Ordine #{ordine.id} confermato!')
                return redirect('ordine_detail', pk=ordine.pk)

        except Exception as e:
            messages.error(request, 'Errore durante il checkout')
            return redirect('cart_detail')

    return render(request, 'core/checkout.html', {'cart': cart})


class OrdineListView(LoginRequiredMixin, ListView):
        model = Ordine
        template_name = 'core/ordine_list.html'
        context_object_name = 'ordini'
        paginate_by = 10

        def get_queryset(self):
            if self.request.user.ruolo == 'ADM' or self.request.user.is_superuser:
                return Ordine.objects.all().order_by('-data_ordine')
            return Ordine.objects.filter(cliente=self.request.user).order_by('-data_ordine')


class OrdineDetailView(LoginRequiredMixin, DetailView):
        model = Ordine
        template_name = 'core/ordine_detail.html'
        context_object_name = 'ordine'

        def get_queryset(self):
            if self.request.user.ruolo == 'ADM' or self.request.user.is_superuser:
                return Ordine.objects.all()
            return Ordine.objects.filter(cliente=self.request.user)
        

class AdminOrdineListView(AdminRequiredMixin, ListView):
    model = Ordine
    template_name = 'core/admin_ordine_list.html'
    context_object_name = 'ordini'
    paginate_by = 20

    def get_queryset(self):
        qs = Ordine.objects.select_related('cliente')

        stato = self.request.GET.get('stato')
        if stato:
            qs = qs.filter(stato=stato)

        return qs.order_by('-data_ordine')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stati'] = Ordine.Stato.choices
        return context


@login_required
def cambia_stato_ordine(request, pk, nuovo_stato):
    if request.user.ruolo != 'ADM':
        return redirect('home')

    ordine = get_object_or_404(Ordine, pk=pk)
    if nuovo_stato in dict(Ordine.Stato.choices):
        ordine.stato = nuovo_stato
        ordine.save()
        messages.success(request, f'Stato ordine aggiornato a {ordine.get_stato_display()}')

    return redirect('admin_ordine_list')