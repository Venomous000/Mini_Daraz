from products.models import Product
from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class CartManager(models.Manager):
    def get_or_create_cart(self, user):
        from .cart_model import Cart  # ← lazy import
        cart, created = Cart.objects.get_or_create(user=user)
        return cart

    def add_item(self, user, product, quantity=1):
        cart = self.get_or_create_cart(user)
        return cart.add_product(product, quantity)

    def merge_session_cart(self, user, session_cart):
        from .cart_model import Cart  # ← lazy import
        cart = self.get_or_create_cart(user)
        for product_id_str, quantity in session_cart.items():
            try:
                product = Product.objects.get(pk=int(product_id_str))
                cart.add_product(product, quantity)
            except (Product.DoesNotExist, ValueError):
                continue
