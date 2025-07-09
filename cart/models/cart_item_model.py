from django.db import models
from products.models import Product


class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name}"

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    def update_quantity(self, quantity):
        if quantity < 1:
            self.delete()
        elif quantity > self.product.stock_quantity:
            raise ValueError(f"Only {self.product.stock_quantity} in stock.")
        else:
            self.quantity = quantity
            self.save()
