from django.db import models
from accounts.models import User
from decimal import Decimal
from .cart_manager import CartManager

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = CartManager()

    def __str__(self):
        return f"Cart of {self.user.email}"

    def update_total_price(self):
        self.total_price = sum(item.total_price for item in self.items.all())
        self.save()

    def is_empty(self):
        return not self.items.exists()

    def clear_if_empty(self):
        if self.is_empty():
            self.delete()

    def add_product(self, product, quantity=1):
        if product.stock_quantity < 1:
            raise ValueError("Product is out of stock.")

        cart_item, created = self.items.get_or_create(
            product=product,
            defaults={'unit_price': product.price_per_piece, 'quantity': quantity}
        )

        if not created:
            if cart_item.quantity + quantity > product.stock_quantity:
                raise ValueError(f"Only {product.stock_quantity} in stock.")
            cart_item.quantity += quantity
            cart_item.save()

        self.update_total_price()
        return cart_item

    def remove_item(self, item_id):
        item = self.items.get(id=item_id)
        item.delete()
        self.update_total_price()
        self.clear_if_empty()

    def update_item_quantity(self, item_id, quantity):
        item = self.items.get(id=item_id)
        item.update_quantity(quantity)
        self.update_total_price()
