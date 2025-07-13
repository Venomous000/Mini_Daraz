from django.db import models
from products.models import Product


class OrderItem(models.Model):
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.quantity} × {self.product.product_name} (${self.subtotal})"

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def total_price(self):
        return self.subtotal

    @classmethod
    def create(cls, order, product, quantity):
        unit_price = product.price_per_piece
        subtotal = unit_price * quantity
        return cls.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=subtotal
        )
