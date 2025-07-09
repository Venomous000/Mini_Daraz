from django.db import models
from products.models import Product


class OrderItem(models.Model):
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name}"

    def total_price(self):
        return self.quantity * self.unit_price
