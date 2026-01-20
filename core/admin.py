from django.contrib import admin
from .models import Categoria, Prodotto, Fornitore, Ordine, OrdineDettaglio
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'attiva')


@admin.register(Prodotto)
class ProdottoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'prezzo', 'codice')
    list_filter = ('categoria',)
    search_fields = ('nome', 'codice')


@admin.register(Fornitore)
class FornitoreAdmin(admin.ModelAdmin):
    list_display = ('ragione_sociale', 'partita_iva', 'email' , 'telefono', 'indirizzo')
    search_fields = ('ragione_sociale', 'partita_iva')
    

@admin.register(OrdineDettaglio)
class OrdineDettaglioAdmin(admin.ModelAdmin):  
    list_display = ('ordine', 'prodotto', 'quantita', 'prezzo_unitario')
    search_fields = ('ordine__id', 'prodotto__nome')
    
@admin.register(Ordine)
class OrdineAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'data_ordine', 'stato', 'totale')
    list_filter = ('stato', 'data_ordine')
    search_fields = ('cliente__username', 'id')
    
    def totale(self, obj):
        return obj.get_total()