from django.db import models
from accounts.models import User
from products.models import Product


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.email} - {self.product.product_name}"

    @classmethod
    def add(cls, user, product):
        obj, created = cls.objects.get_or_create(user=user, product=product)
        if not created:
            raise ValueError("Product is already in wishlist.")
        return obj

    @classmethod
    def remove(cls, user, product_id):
        deleted, _ = cls.objects.filter(user=user, product_id=product_id).delete()
        if not deleted:
            raise ValueError("Item not found in wishlist.")

    @classmethod
    def move_to_cart(cls, user, product):
        from cart.models import Cart

        cart, _ = Cart.objects.get_or_create(user=user)
        cart.add_product(product)  # already handles stock limits
        cls.remove(user, product.id)
