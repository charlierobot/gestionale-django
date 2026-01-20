# core/cart.py
from decimal import Decimal
from urllib import request
from .models import Prodotto
class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, prodotto, quantita=1):
        prodotto_id = str(prodotto.id)
        if prodotto_id not in self.cart:
            self.cart[prodotto_id] = {
                'qty': 0,
                'price': str(prodotto.prezzo)
            }
        self.cart[prodotto_id]['qty'] += quantita
        self.save()

    def save(self):
        self.session.modified = True

    def __len__(self):
        return sum(item['qty'] for item in self.cart.values())

    def remove(self, prodotto):
        prodotto_id = str(prodotto.id)
        if prodotto_id in self.cart:
            del self.cart[prodotto_id]
            self.save()

    def update(self, prodotto, quantita):
        prodotto_id = str(prodotto.id)
        if prodotto_id in self.cart:
            self.cart[prodotto_id]['qty'] = quantita
            self.save()

    def clear(self):
        del self.session['cart']
        self.save()

    def __iter__(self):
        prodotto_ids = self.cart.keys()
        prodotti = Prodotto.objects.filter(id__in=prodotto_ids)
        cart = self.cart.copy()

        for prodotto in prodotti:
            cart[str(prodotto.id)]['prodotto'] = prodotto

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['totale'] = item['price'] * item['qty']
            yield item

    def get_total(self):
        return sum(
            Decimal(item['price']) * item['qty']
            for item in self.cart.values()
        )