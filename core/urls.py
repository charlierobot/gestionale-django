from django.urls import path
from . import views
app_name = 'core'


urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    
    # Dashboards
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/fornitore/', views.dashboard_fornitore, name='dashboard_fornitore'),
    path('dashboard/cliente/', views.dashboard_cliente, name='dashboard_cliente'),
    
    # Product management
    path('prodotti/', views.ProdottoListView.as_view(), name='prodotto_list'),
    path('prodotti/nuovo/', views.ProdottoCreateView.as_view(), name='prodotto_create'),
    path('prodotti/<int:pk>/', views.ProdottoDetailView.as_view(), name='prodotto_detail'),
    path('prodotti/<int:pk>/modifica/', views.ProdottoUpdateView.as_view(), name='prodotto_update'),
    path('prodotti/<int:pk>/elimina/', views.ProdottoDeleteView.as_view(), name='prodotto_delete'),
    
    # Shopping cart
    path('carrello/', views.cart_detail, name='cart_detail'),
    path('carrello/aggiungi/<int:prodotto_id>/', views.add_to_cart, name='add_to_cart'),
    path('carrello/rimuovi/<int:prodotto_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
    
    # Orders
    path('ordini/', views.OrdineListView.as_view(), name='ordini_cliente'),
    path('ordini/<int:pk>/', views.OrdineDetailView.as_view(), name='ordine_detail'),
    
    # Admin order management
    path('admin/ordini/', views.AdminOrdineListView.as_view(), name='admin_ordine_list'),
    path('admin/ordini/<int:pk>/stato/<str:nuovo_stato>/', views.cambia_stato_ordine, name='cambia_stato'),
]